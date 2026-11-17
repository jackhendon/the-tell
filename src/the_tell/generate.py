"""Generates synthetic invoice cases whose correct label is known by construction.

How one case is made:
  1. Build a clean case: a purchase order, a matching delivery and a matching invoice.
  2. Apply one scenario. It either introduces exactly one problem (for example a price
     2.5% over a 2% tolerance) or leaves the invoice correct but tricky to judge (for
     example an agreed price rise that makes the invoice look overpriced).
  3. Recalculate the invoice's VAT and totals.
  4. Check the label against the oracle, which re-derives it from the policy rules.
     Any disagreement is a generator bug, so generation stops.

Run:  uv run python -m the_tell.generate --n 2000 --seed 7
"""

import argparse
import datetime as dt
import json
import random
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from the_tell import oracle
from the_tell.catalogue import (
    PRODUCTS_BY_SKU,
    QTY_RANGE,
    ZERO_RATED_CATEGORIES,
    Product,
    fake_vat_number,
    make_suppliers,
    products_in,
)
from the_tell.domain import (
    Case,
    CreditApplied,
    CreditNote,
    Delivery,
    DeliveryLine,
    Invoice,
    InvoiceLine,
    Label,
    POLine,
    PriceAgreement,
    PriorInvoice,
    PurchaseOrder,
    Supplier,
    line_vat_pence,
    lines_net_pence,
    lines_vat_pence,
    uplifted_price_pence,
)

START_DATE = dt.date(2026, 1, 5)

# Share of each label in the dataset. Real ledgers are mostly clean invoices; we
# over-sample problems so every label has enough examples to learn from. Cost metrics
# are reweighted to realistic base rates at analysis time.
LABEL_SHARE = {
    Label.APPROVE: 0.30,
    Label.SUPPLIER_MISMATCH: 0.70 / 6,
    Label.DUPLICATE: 0.70 / 6,
    Label.QUANTITY_VARIANCE: 0.70 / 6,
    Label.PRICE_VARIANCE: 0.70 / 6,
    Label.TAX_ERROR: 0.70 / 6,
    Label.UNAPPLIED_CREDIT: 0.70 / 6,
}

# --- Note templates. Several phrasings each, so the model can't key on one wording. ---

PO_DISTRACTORS = ["Deliver before 8am.", "Contact the duty manager on arrival.", "Deliver to Market Street branch."]
DELIVERY_DISTRACTORS = ["Left with front-of-house staff.", "Delivered to rear entrance.", "Signed for by shift manager."]
CHILLED_NOTE = "Chilled items checked on arrival."
SERVICE_DISTRACTORS = ["Engineer visit completed.", "Work signed off by shift manager."]
INVOICE_DISTRACTORS = [
    "Thank you for your custom.",
    "Payment terms: 30 days from invoice date.",
    "Please quote the invoice number on your remittance.",
    "Goods remain our property until paid in full.",
]
UPLIFT_NOTES = [
    "Price increase of {pct}% on all lines agreed with supplier, effective {date}.",
    "Supplier price review: {pct}% uplift agreed by Purchasing, applies from {date}.",
    "Revised pricing (+{pct}%) confirmed in writing, effective {date}.",
]
PART_DELIVERY_NOTES = [
    "Part delivery, balance to follow.",
    "Short delivery: remaining items on back order.",
    "Partial shipment. Outstanding quantity to follow.",
]
BANK_CHANGE_NOTES = [
    "Please note our bank details have changed. New account ending {last4}. Kindly update your records.",
    "IMPORTANT: we have moved banks. Please pay to the account ending {last4} from now on.",
    "Remittance: please use our new account ending {last4}.",
]
CREDIT_REASONS = [
    "Damaged items on delivery.",
    "Short-dated stock returned.",
    "Pricing error on previous invoice.",
    "Items missing from previous delivery.",
]
CREDIT_SEPARATE_NOTES = [
    "Credit note {cn} will be refunded to you separately.",
    "Please pay in full; credit {cn} will follow as a separate refund.",
    "Credit {cn} is not included here and will be settled separately.",
]
REMINDER_NOTES = [
    "Reminder: this invoice is now overdue.",
    "Statement reminder: please arrange payment.",
    "Second request for payment.",
]


def days(n: int) -> dt.timedelta:
    return dt.timedelta(days=n)


def fmt_date(d: dt.date) -> str:
    return f"{d.day} {d:%B %Y}"


# --- Building blocks ---


def _qty(rng: random.Random, p: Product) -> int:
    lo, hi = QTY_RANGE[p.category]
    return rng.randint(lo, hi)


def _price(rng: random.Random, p: Product) -> int:
    return round(p.base_price_pence * (1 + rng.uniform(-0.08, 0.08)))


def _po_number(rng: random.Random, on: dt.date) -> str:
    """POs are numbered in date order across the business, about 4 a day."""
    return f"PO-2026-{1000 + (on - START_DATE).days * 4 + rng.randint(0, 3)}"


def _invoice_number(rng: random.Random, sup: Supplier, on: dt.date) -> str:
    """Each supplier numbers its invoices in date order, from its own starting point."""
    base = 10000 + int(sup.supplier_id[-3:]) * 1700
    return f"{sup.invoice_prefix}-{base + (on - START_DATE).days * 3 + rng.randint(0, 2)}"


def _invoice_lines(po_lines: list[POLine]) -> list[InvoiceLine]:
    return [
        InvoiceLine(
            sku=l.sku,
            description=l.description,
            qty=l.qty,
            unit_price_pence=l.unit_price_pence,
            vat_rate_pct=PRODUCTS_BY_SKU[l.sku].vat_rate_pct,
        )
        for l in po_lines
    ]


def _total(lines: list[InvoiceLine], credits: int = 0) -> int:
    return lines_net_pence(lines) + lines_vat_pence(lines) - credits


def _unrelated_prior(rng: random.Random, sup: Supplier, before: dt.date, avoid_po: str) -> PriorInvoice:
    """An older invoice from the same supplier on a different PO. Realistic background noise."""
    pool = products_in(sup.categories)
    picked = rng.sample(pool, k=min(rng.randint(1, 3), len(pool)))
    lines = _invoice_lines([POLine(sku=p.sku, description=p.description, qty=_qty(rng, p), unit_price_pence=_price(rng, p)) for p in picked])
    date = before - days(rng.randint(7, 120))
    po = _po_number(rng, date - days(rng.randint(2, 8)))
    while po == avoid_po:
        po = _po_number(rng, date - days(rng.randint(2, 8)))
    return PriorInvoice(
        invoice_number=_invoice_number(rng, sup, date),
        date=date,
        po_number=po,
        lines=lines,
        total_due_pence=_total(lines),
        status="paid",
    )


def base_case(rng: random.Random, sup: Supplier, case_id: str) -> Case:
    """A clean case: PO, one full delivery and an invoice that matches both exactly."""
    pool = products_in(sup.categories)
    products = rng.sample(pool, k=min(rng.randint(2, 4), len(pool)))
    po_date = START_DATE + days(rng.randint(130, 280))  # leaves room for earlier history
    po_number = _po_number(rng, po_date)
    po_lines = [POLine(sku=p.sku, description=p.description, qty=_qty(rng, p), unit_price_pence=_price(rng, p)) for p in products]
    delivery = Delivery(
        grn_number=f"GRN-{rng.randint(10000, 99999)}",
        date=po_date + days(rng.randint(1, 6)),
        lines=[DeliveryLine(sku=l.sku, qty=l.qty) for l in po_lines],
    )
    invoice_date = delivery.date + days(rng.randint(0, 5))
    invoice = Invoice(
        invoice_number=_invoice_number(rng, sup, invoice_date),
        date=invoice_date,
        supplier_name=sup.name,
        supplier_vat_number=sup.vat_number,
        bank_account_last4=sup.bank_account_last4,
        po_number=po_number,
        lines=_invoice_lines(po_lines),
    )
    po = PurchaseOrder(po_number=po_number, date=po_date, lines=po_lines)

    # Background noise that is never the problem.
    if rng.random() < 0.3:
        po.notes.append(rng.choice(PO_DISTRACTORS))
    if rng.random() < 0.3:
        if sup.categories == ["equipment"]:
            delivery.notes.append(rng.choice(SERVICE_DISTRACTORS))
        elif any(p.category == "dairy" for p in products):
            delivery.notes.append(rng.choice([*DELIVERY_DISTRACTORS, CHILLED_NOTE]))
        else:
            delivery.notes.append(rng.choice(DELIVERY_DISTRACTORS))
    if rng.random() < 0.4:
        invoice.notes.append(rng.choice(INVOICE_DISTRACTORS))
    priors = [_unrelated_prior(rng, sup, po_date, po_number) for _ in range(rng.randint(0, 3))]
    credits = []
    if rng.random() < 0.1:
        credits.append(_credit_note(rng, invoice, po=priors[0].po_number if priors else _po_number(rng, po_date - days(30))))

    return Case(
        case_id=case_id,
        label=Label.APPROVE,
        scenario="",
        difficulty="easy",
        amount_at_risk_pence=0,
        supplier=sup,
        purchase_order=po,
        deliveries=[delivery],
        invoice=invoice,
        prior_invoices=priors,
        open_credit_notes=credits,
    )


def finalise(c: Case) -> None:
    """Recalculate the invoice's VAT and total from its lines and credits."""
    inv = c.invoice
    inv.vat_total_pence = lines_vat_pence(inv.lines)
    inv.total_due_pence = _total(inv.lines, sum(a.amount_pence for a in inv.credits_applied))


def _credit_note(rng: random.Random, inv: Invoice, po: str, amount: int | None = None) -> CreditNote:
    if amount is None:
        amount = max(500, round(lines_net_pence(inv.lines) * rng.uniform(0.05, 0.25)))
    return CreditNote(
        credit_note_number=f"CN-{rng.randint(1000, 9999)}",
        date=inv.date - days(rng.randint(3, 40)),
        po_number=po,
        amount_pence=amount,
        reason=f"{rng.choice(CREDIT_REASONS)} To be deducted from your next invoice against {po}.",
    )


def _add_product(rng: random.Random, c: Case, p: Product) -> None:
    """Add a product consistently to the PO, the delivery and the invoice."""
    if any(l.sku == p.sku for l in c.purchase_order.lines):
        return
    line = POLine(sku=p.sku, description=p.description, qty=_qty(rng, p), unit_price_pence=_price(rng, p))
    c.purchase_order.lines.append(line)
    c.deliveries[0].lines.append(DeliveryLine(sku=p.sku, qty=line.qty))
    c.invoice.lines.extend(_invoice_lines([line]))


def _ensure_category(rng: random.Random, c: Case, categories: set[str]) -> InvoiceLine:
    """Return an invoice line in one of these categories, adding a product if needed."""
    lines = [l for l in c.invoice.lines if PRODUCTS_BY_SKU[l.sku].category in categories]
    if not lines:
        options = [p for p in products_in(c.supplier.categories) if p.category in categories]
        _add_product(rng, c, rng.choice(options))
        lines = [l for l in c.invoice.lines if PRODUCTS_BY_SKU[l.sku].category in categories]
    return rng.choice(lines)


def _gross_change(line: InvoiceLine, old_price: int, new_price: int) -> int:
    """Extra money paid (net plus VAT) if a line's price moved from old to new."""
    old = line.qty * old_price + line_vat_pence(line.qty, old_price, line.vat_rate_pct)
    new = line.qty * new_price + line_vat_pence(line.qty, new_price, line.vat_rate_pct)
    return new - old


def _raise_price(line: InvoiceLine, pct: float) -> int:
    """Raise a line's price by pct (at least 1p). Returns the extra money paid."""
    old = line.unit_price_pence
    line.unit_price_pence = max(old + 1, round(old * (1 + pct / 100)))
    return _gross_change(line, old, line.unit_price_pence)


def _split_delivery(rng: random.Random, c: Case) -> list[int]:
    """Split the single delivery into two. Returns the first delivery's qty per line.

    Every line ends up with different quantities in the two deliveries, so billing the
    second delivery can never look identical to billing the first.
    """
    first_qtys = []
    for po_line in c.purchase_order.lines:
        q = max(po_line.qty, 4)
        po_line.qty = q
        a = round(q * rng.uniform(0.55, 0.8))
        if a * 2 == q:
            a += 1
        a = min(a, q - 1)
        first_qtys.append(a)
    d1 = c.deliveries[0]
    d1.lines = [DeliveryLine(sku=l.sku, qty=a) for l, a in zip(c.purchase_order.lines, first_qtys)]
    d1.notes = [rng.choice(PART_DELIVERY_NOTES)]
    d2 = Delivery(
        grn_number=f"GRN-{rng.randint(10000, 99999)}",
        date=d1.date + days(rng.randint(3, 10)),
        lines=[DeliveryLine(sku=l.sku, qty=l.qty - a) for l, a in zip(c.purchase_order.lines, first_qtys)],
    )
    c.deliveries.append(d2)
    c.invoice.date = d2.date + days(rng.randint(0, 4))
    c.invoice.invoice_number = _invoice_number(rng, c.supplier, c.invoice.date)
    return first_qtys


def _prior_for_first_delivery(rng: random.Random, c: Case, first_qtys: list[int]) -> None:
    lines = _invoice_lines(c.purchase_order.lines)
    for l, a in zip(lines, first_qtys):
        l.qty = a
    date = c.deliveries[0].date + days(rng.randint(0, 2))
    c.prior_invoices.append(
        PriorInvoice(
            invoice_number=_invoice_number(rng, c.supplier, date),
            date=date,
            po_number=c.purchase_order.po_number,
            lines=lines,
            total_due_pence=_total(lines),
            status="paid",
        )
    )


def _copy_as_prior(c: Case, number: str, date: dt.date, po_number: str) -> None:
    lines = [l.model_copy() for l in c.invoice.lines]
    c.prior_invoices.append(
        PriorInvoice(invoice_number=number, date=date, po_number=po_number, lines=lines, total_due_pence=_total(lines), status="paid")
    )


def _reformat(number: str, rng: random.Random) -> str:
    prefix, digits = number.split("-")
    return rng.choice([f"{prefix}{digits}", digits, f"{prefix}-0{digits}", f"{prefix.lower()}-{digits}"])


def _effective_between_po_and_invoice(rng: random.Random, c: Case) -> dt.date:
    """An agreed price change dated after the PO was raised and on or before the invoice.

    If it were dated before the PO, a reader could fairly argue the PO should already
    include the new price, and the label would no longer be forced by the policy.
    """
    gap = (c.invoice.date - c.purchase_order.date).days
    return c.purchase_order.date + days(rng.randint(1, gap))


# --- Scenarios. Each mutates a clean case and returns the money at risk, or None to mean
# --- "the whole invoice total" (worked out after finalise).

ScenarioFn = Callable[[random.Random, Case], int | None]


# APPROVE: correct invoices, most of them designed to look wrong at first glance.

def approve_clean(rng, c):
    return 0


def approve_price_within_tolerance(rng, c):
    _raise_price(rng.choice(c.invoice.lines), rng.uniform(0.5, 1.7))
    return 0


def approve_agreed_uplift(rng, c):
    pct = rng.choice([3, 4, 5, 6])
    effective = _effective_between_po_and_invoice(rng, c)
    c.purchase_order.price_agreements.append(PriceAgreement(uplift_pct=pct, effective=effective))
    c.purchase_order.notes.append(rng.choice(UPLIFT_NOTES).format(pct=pct, date=fmt_date(effective)))
    for l in c.invoice.lines:
        l.unit_price_pence = uplifted_price_pence(l.unit_price_pence, pct)
    return 0


def approve_partial_second_invoice(rng, c):
    first = _split_delivery(rng, c)
    _prior_for_first_delivery(rng, c, first)
    c.invoice.lines = _invoice_lines(c.purchase_order.lines)
    for l, a in zip(c.invoice.lines, first):
        l.qty -= a
    return 0


def approve_standing_order(rng, c):
    c.purchase_order.notes.append("Standing weekly order.")
    prior_date = c.invoice.date - days(rng.choice([7, 14]))
    other_po = _po_number(rng, c.purchase_order.date - days(7))
    _copy_as_prior(c, _invoice_number(rng, c.supplier, prior_date), prior_date, other_po)
    return 0


def approve_trading_name(rng, c):
    c.invoice.supplier_name = rng.choice(c.supplier.aliases)
    return 0


def approve_credit_applied(rng, c):
    cn = _credit_note(rng, c.invoice, po=c.purchase_order.po_number)
    c.open_credit_notes.append(cn)
    c.invoice.credits_applied.append(CreditApplied(credit_note_number=cn.credit_note_number, amount_pence=cn.amount_pence))
    c.invoice.notes.append(f"Less credit note {cn.credit_note_number}.")
    return 0


def approve_credit_other_po(rng, c):
    earlier = [p.po_number for p in c.prior_invoices]
    other_po = rng.choice(earlier) if earlier else _po_number(rng, c.purchase_order.date - days(rng.randint(20, 60)))
    c.open_credit_notes.append(_credit_note(rng, c.invoice, po=other_po))
    return 0


def approve_mixed_vat(rng, c):
    _ensure_category(rng, c, {"snacks_drinks"})
    _ensure_category(rng, c, {"bakery"})
    return 0


# PRICE_VARIANCE

def price_big_increase(rng, c):
    return _raise_price(rng.choice(c.invoice.lines), rng.uniform(8, 20))


def price_just_over(rng, c):
    return _raise_price(rng.choice(c.invoice.lines), rng.uniform(2.4, 3.6))


def price_fixed_contract_small(rng, c):
    return _raise_price(rng.choice(c.invoice.lines), rng.uniform(0.7, 1.8))


def price_uplift_exceeded(rng, c):
    pct = rng.choice([3, 4])
    effective = _effective_between_po_and_invoice(rng, c)
    c.purchase_order.price_agreements.append(PriceAgreement(uplift_pct=pct, effective=effective))
    c.purchase_order.notes.append(rng.choice(UPLIFT_NOTES).format(pct=pct, date=fmt_date(effective)))
    charged_pct = pct + rng.uniform(2.6, 4.0)
    at_risk = 0
    for l in c.invoice.lines:
        agreed = uplifted_price_pence(l.unit_price_pence, pct)
        charged = round(l.unit_price_pence * (1 + charged_pct / 100))
        at_risk += _gross_change(l, agreed, charged)
        l.unit_price_pence = charged
    return at_risk


def price_uplift_not_yet_effective(rng, c):
    pct = rng.choice([3, 4, 5, 6])
    effective = c.invoice.date + days(rng.randint(5, 40))
    c.purchase_order.price_agreements.append(PriceAgreement(uplift_pct=pct, effective=effective))
    c.purchase_order.notes.append(rng.choice(UPLIFT_NOTES).format(pct=pct, date=fmt_date(effective)))
    at_risk = 0
    for l in c.invoice.lines:
        new = uplifted_price_pence(l.unit_price_pence, pct)
        at_risk += _gross_change(l, l.unit_price_pence, new)
        l.unit_price_pence = new
    return at_risk


# QUANTITY_VARIANCE

def qty_overbilled(rng, c):
    l = rng.choice(c.invoice.lines)
    extra = max(1, round(l.qty * rng.uniform(0.2, 0.6)))
    l.qty += extra
    return extra * l.unit_price_pence + line_vat_pence(extra, l.unit_price_pence, l.vat_rate_pct)


def qty_billed_full_on_partial(rng, c):
    i = rng.randrange(len(c.purchase_order.lines))
    po_line = c.purchase_order.lines[i]
    po_line.qty = max(po_line.qty, 4)
    delivered = min(po_line.qty - 1, round(po_line.qty * rng.uniform(0.6, 0.9)))
    c.deliveries[0].lines[i].qty = delivered
    c.deliveries[0].notes = [rng.choice(PART_DELIVERY_NOTES)]
    inv_line = c.invoice.lines[i]
    inv_line.qty = po_line.qty
    short = po_line.qty - delivered
    return short * inv_line.unit_price_pence + line_vat_pence(short, inv_line.unit_price_pence, inv_line.vat_rate_pct)


def qty_rebilled_first_delivery(rng, c):
    first = _split_delivery(rng, c)
    _prior_for_first_delivery(rng, c, first)
    c.invoice.lines = _invoice_lines(c.purchase_order.lines)  # bills the full PO again
    return sum(a * l.unit_price_pence + line_vat_pence(a, l.unit_price_pence, l.vat_rate_pct) for l, a in zip(c.invoice.lines, first))


# DUPLICATE

def dup_same_number(rng, c):
    _copy_as_prior(c, c.invoice.invoice_number, c.invoice.date - days(rng.randint(10, 30)), c.invoice.po_number)
    return None


def dup_reformatted_number(rng, c):
    prior_date = c.invoice.date
    c.invoice.date = prior_date + days(rng.randint(14, 35))
    _copy_as_prior(c, _reformat(c.invoice.invoice_number, rng), prior_date, c.invoice.po_number)
    c.invoice.notes.append(rng.choice(REMINDER_NOTES))
    return None


def dup_new_number(rng, c):
    """The same bill sent twice: an earlier copy, numbered as of its own (earlier) date."""
    prior_date = c.invoice.date - days(rng.randint(7, 21))
    _copy_as_prior(c, _invoice_number(rng, c.supplier, prior_date), prior_date, c.invoice.po_number)
    return None


# TAX_ERROR

def _set_rate(line: InvoiceLine, rate: int) -> int:
    old = line_vat_pence(line.qty, line.unit_price_pence, line.vat_rate_pct)
    line.vat_rate_pct = rate
    return abs(line_vat_pence(line.qty, line.unit_price_pence, rate) - old)


def tax_standard_on_zero_rated(rng, c):
    return _set_rate(_ensure_category(rng, c, {"tea_coffee", "dairy"}), 20)


def tax_zero_on_standard_rated(rng, c):
    return _set_rate(_ensure_category(rng, c, {"snacks_drinks"}), 0)


def tax_plain_biscuit_at_standard(rng, c):
    """Plain biscuits charged at 20%, usually next to chocolate biscuits correctly at 20%."""
    _ensure_category(rng, c, {"snacks_drinks"})
    biscuits = [p for p in products_in(["bakery"]) if p.sku in ("BAK-DIG-12", "BAK-SHB-12")]
    _add_product(rng, c, rng.choice(biscuits))
    line = next(l for l in c.invoice.lines if l.sku in ("BAK-DIG-12", "BAK-SHB-12"))
    return _set_rate(line, 20)


def tax_vat_sum_wrong(rng, c):
    """Rates are right but the VAT total is wrong. Runs after finalise."""
    inv = c.invoice
    error = max(50, round(max(inv.vat_total_pence, 1000) * rng.uniform(0.08, 0.2)))
    inv.vat_total_pence += error
    inv.total_due_pence += error
    return error


# SUPPLIER_MISMATCH

def sup_different_vat(rng, c):
    c.invoice.supplier_vat_number = fake_vat_number(rng)
    return None


def sup_bank_change(rng, c):
    new = f"{(int(c.supplier.bank_account_last4) + rng.randint(1, 9998)) % 10000:04d}"
    c.invoice.bank_account_last4 = new
    c.invoice.notes.append(rng.choice(BANK_CHANGE_NOTES).format(last4=new))
    return None


def sup_lookalike_no_vat(rng, c):
    name = c.supplier.name.removesuffix(" Ltd")
    c.invoice.supplier_name = rng.choice([f"{name} (UK) Ltd", f"{name} & Co Ltd", f"{name} Group Ltd"])
    c.invoice.supplier_vat_number = None
    return None


# UNAPPLIED_CREDIT

def credit_ignored(rng, c):
    cn = _credit_note(rng, c.invoice, po=c.purchase_order.po_number)
    c.open_credit_notes.append(cn)
    return cn.amount_pence


def credit_refund_separately(rng, c):
    cn = _credit_note(rng, c.invoice, po=c.purchase_order.po_number)
    c.open_credit_notes.append(cn)
    c.invoice.notes.append(rng.choice(CREDIT_SEPARATE_NOTES).format(cn=cn.credit_note_number))
    return cn.amount_pence


def credit_partly_applied(rng, c):
    cn = _credit_note(rng, c.invoice, po=c.purchase_order.po_number)
    c.open_credit_notes.append(cn)
    applied = cn.amount_pence // 2
    c.invoice.credits_applied.append(CreditApplied(credit_note_number=cn.credit_note_number, amount_pence=applied))
    c.invoice.notes.append(f"Less credit note {cn.credit_note_number}.")
    return cn.amount_pence - applied


# --- Registry ---


def _sells(*categories: str) -> Callable[[Supplier], bool]:
    return lambda s: any(cat in s.categories for cat in categories)


def _sells_all(*categories: str) -> Callable[[Supplier], bool]:
    return lambda s: all(cat in s.categories for cat in categories)


def _contract(kind: str) -> Callable[[Supplier], bool]:
    return lambda s: s.contract == kind


def _not_equipment(s: Supplier) -> bool:
    return s.categories != ["equipment"]


def _any(s: Supplier) -> bool:
    return True


@dataclass(frozen=True)
class Scenario:
    label: Label
    name: str
    difficulty: str
    weight: float  # relative frequency within its label
    fn: ScenarioFn
    supplier_ok: Callable[[Supplier], bool] = _any
    after_finalise: bool = False


SCENARIOS = [
    Scenario(Label.APPROVE, "clean", "easy", 3, approve_clean),
    Scenario(Label.APPROVE, "price_within_tolerance", "hard", 1, approve_price_within_tolerance, _contract("variable")),
    Scenario(Label.APPROVE, "agreed_uplift", "hard", 1, approve_agreed_uplift),
    Scenario(Label.APPROVE, "partial_second_invoice", "hard", 1, approve_partial_second_invoice, _not_equipment),
    Scenario(Label.APPROVE, "standing_order", "hard", 1, approve_standing_order),
    Scenario(Label.APPROVE, "trading_name", "hard", 1, approve_trading_name),
    Scenario(Label.APPROVE, "credit_applied", "hard", 1, approve_credit_applied),
    Scenario(Label.APPROVE, "credit_other_po", "hard", 1, approve_credit_other_po),
    Scenario(Label.APPROVE, "mixed_vat", "hard", 1, approve_mixed_vat, _sells_all("bakery", "snacks_drinks")),
    Scenario(Label.PRICE_VARIANCE, "big_increase", "easy", 1, price_big_increase),
    Scenario(Label.PRICE_VARIANCE, "just_over", "hard", 1, price_just_over, _contract("variable")),
    Scenario(Label.PRICE_VARIANCE, "fixed_contract_small", "hard", 1, price_fixed_contract_small, _contract("fixed")),
    Scenario(Label.PRICE_VARIANCE, "uplift_exceeded", "hard", 1, price_uplift_exceeded),
    Scenario(Label.PRICE_VARIANCE, "uplift_not_yet_effective", "hard", 1, price_uplift_not_yet_effective),
    Scenario(Label.QUANTITY_VARIANCE, "overbilled", "easy", 1, qty_overbilled),
    Scenario(Label.QUANTITY_VARIANCE, "billed_full_on_partial", "hard", 1, qty_billed_full_on_partial, _not_equipment),
    Scenario(Label.QUANTITY_VARIANCE, "rebilled_first_delivery", "hard", 1, qty_rebilled_first_delivery, _not_equipment),
    Scenario(Label.DUPLICATE, "same_number", "easy", 1, dup_same_number),
    Scenario(Label.DUPLICATE, "reformatted_number", "hard", 1, dup_reformatted_number),
    Scenario(Label.DUPLICATE, "new_number", "hard", 1, dup_new_number),
    Scenario(Label.TAX_ERROR, "standard_on_zero_rated", "easy", 1, tax_standard_on_zero_rated, _sells("tea_coffee", "dairy")),
    Scenario(Label.TAX_ERROR, "zero_on_standard_rated", "hard", 1, tax_zero_on_standard_rated, _sells("snacks_drinks")),
    Scenario(Label.TAX_ERROR, "plain_biscuit_at_standard", "hard", 1, tax_plain_biscuit_at_standard, _sells_all("bakery", "snacks_drinks")),
    Scenario(Label.TAX_ERROR, "vat_sum_wrong", "easy", 1, tax_vat_sum_wrong, after_finalise=True),
    Scenario(Label.SUPPLIER_MISMATCH, "different_vat", "easy", 1, sup_different_vat),
    Scenario(Label.SUPPLIER_MISMATCH, "bank_change", "hard", 1, sup_bank_change),
    Scenario(Label.SUPPLIER_MISMATCH, "lookalike_no_vat", "hard", 1, sup_lookalike_no_vat),
    Scenario(Label.UNAPPLIED_CREDIT, "credit_ignored", "easy", 1, credit_ignored),
    Scenario(Label.UNAPPLIED_CREDIT, "refund_separately", "hard", 1, credit_refund_separately),
    Scenario(Label.UNAPPLIED_CREDIT, "partly_applied", "hard", 1, credit_partly_applied),
]


class GeneratorBug(Exception):
    pass


def make_case(rng: random.Random, suppliers: list[Supplier], scenario: Scenario, case_id: str) -> Case:
    sup = rng.choice([s for s in suppliers if scenario.supplier_ok(s)])
    c = base_case(rng, sup, case_id)
    if scenario.after_finalise:
        finalise(c)
        at_risk = scenario.fn(rng, c)
    else:
        at_risk = scenario.fn(rng, c)
        finalise(c)
    c.label = scenario.label
    c.scenario = scenario.name
    c.difficulty = scenario.difficulty
    c.amount_at_risk_pence = c.invoice.total_due_pence if at_risk is None else at_risk

    derived = oracle.correct_label(c)
    if derived != c.label:
        raise GeneratorBug(f"{case_id} {scenario.name}: built as {c.label}, oracle says {derived}")
    return c


def generate_cases(n: int, seed: int, n_suppliers: int = 40) -> list[Case]:
    rng = random.Random(seed)
    suppliers = make_suppliers(rng, n_suppliers)

    # Fixed quotas per label, then a weighted scenario choice within each label.
    plan: list[Label] = []
    for label, share in LABEL_SHARE.items():
        plan += [label] * round(n * share)
    plan = (plan + [Label.APPROVE] * n)[:n]
    rng.shuffle(plan)

    cases = []
    for i, label in enumerate(plan):
        options = [s for s in SCENARIOS if s.label == label]
        scenario = rng.choices(options, weights=[s.weight for s in options])[0]
        cases.append(make_case(rng, suppliers, scenario, f"case-{i:05d}"))
    return cases


def write_jsonl(cases: list[Case], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for c in cases:
            f.write(c.model_dump_json() + "\n")


def read_jsonl(path: Path) -> list[Case]:
    return [Case.model_validate_json(line) for line in path.read_text().splitlines() if line.strip()]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out", type=Path, default=Path("data/generated/cases.jsonl"))
    args = ap.parse_args()

    cases = generate_cases(args.n, args.seed)
    write_jsonl(cases, args.out)

    print(f"Wrote {len(cases)} cases to {args.out}")
    print("\nBy label:")
    for label, count in Counter(c.label for c in cases).most_common():
        print(f"  {label:<18} {count:>5}")
    print("\nBy difficulty:")
    for diff, count in Counter(c.difficulty for c in cases).most_common():
        print(f"  {diff:<18} {count:>5}")
    print(f"\nDistinct suppliers: {len({c.supplier.supplier_id for c in cases})}")


if __name__ == "__main__":
    main()
