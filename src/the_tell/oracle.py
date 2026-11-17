"""Works out the correct label for a case directly from the structured data and the policy.

This is a second, independent path to the answer. The generator decides the label by
construction; the oracle re-derives it by applying the policy rules. If they ever
disagree, the generator has a bug, and generation stops.
"""

from collections import Counter

from the_tell.catalogue import PRODUCTS_BY_SKU
from the_tell.domain import Case, Label, lines_vat_pence, uplifted_price_pence
from the_tell.policy import PRECEDENCE, PRICE_TOLERANCE_PCT


def supplier_mismatch(c: Case) -> bool:
    inv, sup = c.invoice, c.supplier
    return inv.supplier_vat_number != sup.vat_number or inv.bank_account_last4 != sup.bank_account_last4


def duplicate(c: Case) -> bool:
    def bill(lines):
        return sorted((l.sku, l.qty, l.unit_price_pence) for l in lines)

    return any(
        p.po_number == c.invoice.po_number and bill(p.lines) == bill(c.invoice.lines)
        for p in c.prior_invoices
    )


def quantity_variance(c: Case) -> bool:
    delivered = Counter()
    for d in c.deliveries:
        for l in d.lines:
            delivered[l.sku] += l.qty
    invoiced = Counter()
    for inv in [c.invoice, *[p for p in c.prior_invoices if p.po_number == c.invoice.po_number]]:
        for l in inv.lines:
            invoiced[l.sku] += l.qty
    return any(invoiced[sku] > delivered[sku] for sku in invoiced)


def price_variance(c: Case) -> bool:
    po_price = {l.sku: l.unit_price_pence for l in c.purchase_order.lines}
    in_force = [a for a in c.purchase_order.price_agreements if a.effective <= c.invoice.date]
    uplift = max(in_force, key=lambda a: a.effective).uplift_pct if in_force else 0
    tolerance = PRICE_TOLERANCE_PCT[c.supplier.contract]
    for l in c.invoice.lines:
        expected = uplifted_price_pence(po_price[l.sku], uplift)
        # Integer form of: (charged - expected) / expected * 100 > tolerance
        if (l.unit_price_pence - expected) * 100 > tolerance * expected:
            return True
    return False


def tax_error(c: Case) -> bool:
    wrong_rate = any(l.vat_rate_pct != PRODUCTS_BY_SKU[l.sku].vat_rate_pct for l in c.invoice.lines)
    wrong_sum = c.invoice.vat_total_pence != lines_vat_pence(c.invoice.lines)
    return wrong_rate or wrong_sum


def unapplied_credit(c: Case) -> bool:
    for cn in c.open_credit_notes:
        if cn.po_number != c.invoice.po_number:
            continue
        applied = sum(a.amount_pence for a in c.invoice.credits_applied if a.credit_note_number == cn.credit_note_number)
        if applied < cn.amount_pence:
            return True
    return False


CHECKS = {
    Label.SUPPLIER_MISMATCH: supplier_mismatch,
    Label.DUPLICATE: duplicate,
    Label.QUANTITY_VARIANCE: quantity_variance,
    Label.PRICE_VARIANCE: price_variance,
    Label.TAX_ERROR: tax_error,
    Label.UNAPPLIED_CREDIT: unapplied_credit,
}


def issues(c: Case) -> list[Label]:
    """Every problem present, in policy precedence order."""
    return [label for label in PRECEDENCE if CHECKS[label](c)]


def correct_label(c: Case) -> Label:
    found = issues(c)
    return found[0] if found else Label.APPROVE
