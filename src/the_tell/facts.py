"""Deterministic pre-checks: the arithmetic and matching an AP system would do.

They state facts, never verdicts. "Invoiced £15.81 against PO £15.54, +1.7%" is a fact.
"Price above tolerance" would be a verdict, and would leave the model nothing to judge.

Rule of thumb: code does what a spreadsheet could do; the model does whatever needs the
policy. So code never applies a tolerance, reads a note, decides which VAT rate an item
should have, or decides whether a credit should be deducted.
"""

from collections import Counter
from dataclasses import dataclass

from the_tell.domain import Case, fmt_money, lines_vat_pence


@dataclass
class LineFacts:
    sku: str
    po_price_pence: int
    invoiced_price_pence: int
    ordered: int
    received: int
    invoiced_earlier: int  # on earlier invoices against this PO
    invoiced_now: int

    @property
    def price_change_pct(self) -> float:
        return (self.invoiced_price_pence - self.po_price_pence) * 100 / self.po_price_pence

    @property
    def invoiced_total(self) -> int:
        return self.invoiced_earlier + self.invoiced_now


@dataclass
class Facts:
    name_match: str  # "registered name" | "listed trading name" | "neither"
    vat_number: str  # "same as record" | "different from record" | "not shown on invoice"
    bank_account: str  # "same as record" | "different from record"
    lines: list[LineFacts]
    earlier_same_po: list[tuple[str, bool]]  # (invoice number, identical lines?)
    identical_other_po: list[tuple[str, str]]  # (invoice number, PO) with identical lines
    vat_recalculated_pence: int  # from the rates charged, not the correct rates
    vat_stated_pence: int
    credits_this_po: list[tuple[str, int, int]]  # (credit note, amount, deducted here)
    credits_other_po: list[tuple[str, str]]  # (credit note, PO)


def _bill(lines) -> list[tuple]:
    return sorted((l.sku, l.qty, l.unit_price_pence) for l in lines)


def compute(c: Case) -> Facts:
    inv, sup, po = c.invoice, c.supplier, c.purchase_order

    if inv.supplier_name == sup.name:
        name = "registered name"
    elif inv.supplier_name in sup.aliases:
        name = "listed trading name"
    else:
        name = "neither"

    if inv.supplier_vat_number is None:
        vat = "not shown on invoice"
    else:
        vat = "same as record" if inv.supplier_vat_number == sup.vat_number else "different from record"
    bank = "same as record" if inv.bank_account_last4 == sup.bank_account_last4 else "different from record"

    received = Counter()
    for d in c.deliveries:
        for l in d.lines:
            received[l.sku] += l.qty
    earlier = [p for p in c.prior_invoices if p.po_number == inv.po_number]
    invoiced_earlier = Counter()
    for p in earlier:
        for l in p.lines:
            invoiced_earlier[l.sku] += l.qty
    po_lines = {l.sku: l for l in po.lines}
    lines = [
        LineFacts(
            sku=l.sku,
            po_price_pence=po_lines[l.sku].unit_price_pence,
            invoiced_price_pence=l.unit_price_pence,
            ordered=po_lines[l.sku].qty,
            received=received[l.sku],
            invoiced_earlier=invoiced_earlier[l.sku],
            invoiced_now=l.qty,
        )
        for l in inv.lines
    ]

    this_bill = _bill(inv.lines)
    return Facts(
        name_match=name,
        vat_number=vat,
        bank_account=bank,
        lines=lines,
        earlier_same_po=[(p.invoice_number, _bill(p.lines) == this_bill) for p in sorted(earlier, key=lambda p: p.date)],
        identical_other_po=[
            (p.invoice_number, p.po_number)
            for p in c.prior_invoices
            if p.po_number != inv.po_number and _bill(p.lines) == this_bill
        ],
        vat_recalculated_pence=lines_vat_pence(inv.lines),
        vat_stated_pence=inv.vat_total_pence,
        credits_this_po=[
            (
                cn.credit_note_number,
                cn.amount_pence,
                sum(a.amount_pence for a in inv.credits_applied if a.credit_note_number == cn.credit_note_number),
            )
            for cn in c.open_credit_notes
            if cn.po_number == inv.po_number
        ],
        credits_other_po=[(cn.credit_note_number, cn.po_number) for cn in c.open_credit_notes if cn.po_number != inv.po_number],
    )


def render_facts(f: Facts) -> str:
    out = ["AUTOMATED CHECKS (calculated by the AP system from the documents above)"]

    out.append("  Supplier:")
    out.append(f"    Name on invoice matches: {f.name_match}")
    out.append(f"    VAT number on invoice: {f.vat_number}")
    out.append(f"    Bank account on invoice: {f.bank_account}")

    out.append("  Prices (invoice against purchase order):")
    for l in f.lines:
        out.append(
            f"    {l.sku:<14} PO {fmt_money(l.po_price_pence):>9}  invoiced {fmt_money(l.invoiced_price_pence):>9}  change {l.price_change_pct:+.1f}%"
        )

    out.append("  Quantities on this PO:")
    for l in f.lines:
        out.append(
            f"    {l.sku:<14} ordered {l.ordered:>3}  received {l.received:>3}  "
            f"invoiced earlier {l.invoiced_earlier:>3}  this invoice {l.invoiced_now:>3}  total invoiced {l.invoiced_total:>3}"
        )

    out.append("  Earlier invoices on this PO:")
    if not f.earlier_same_po:
        out.append("    (none)")
    for number, identical in f.earlier_same_po:
        out.append(f"    {number}: items, quantities and prices identical to this invoice: {'yes' if identical else 'no'}")
    if f.identical_other_po:
        out.append("  Earlier invoices on other POs with items, quantities and prices identical to this invoice:")
        for number, po in f.identical_other_po:
            out.append(f"    {number} (PO {po})")

    out.append("  VAT:")
    out.append(f"    Sum of VAT on each line, at the rates charged: {fmt_money(f.vat_recalculated_pence)}")
    out.append(f"    VAT total stated on invoice: {fmt_money(f.vat_stated_pence)}")

    out.append("  Open credit notes referencing this PO:")
    if not f.credits_this_po:
        out.append("    (none)")
    for cn, amount, deducted in f.credits_this_po:
        out.append(f"    {cn}: {fmt_money(amount)}, deducted on this invoice: {fmt_money(deducted)}")
    if f.credits_other_po:
        out.append("  Open credit notes referencing other POs:")
        for cn, po in f.credits_other_po:
            out.append(f"    {cn} (PO {po})")

    return "\n".join(out)
