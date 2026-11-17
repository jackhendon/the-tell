"""Turns a case into the plain-text documents a reviewer sees.

The same text goes to you (in the review sample) and to the model (in step 2), so
anything the model is judged on is something a human could see too. The label,
scenario and amount at risk are never rendered here.
"""

from the_tell.domain import Case, InvoiceLine, fmt_money, line_net_pence


def _d(d) -> str:
    return f"{d.day} {d:%b %Y}"


def _invoice_lines(lines: list[InvoiceLine]) -> list[str]:
    out = []
    for l in lines:
        net = fmt_money(line_net_pence(l.qty, l.unit_price_pence))
        out.append(f"  {l.sku:<14} {l.description:<48} qty {l.qty:>3} @ {fmt_money(l.unit_price_pence):>9}  VAT {l.vat_rate_pct:>2}%  net {net:>10}")
    return out


def render_case(c: Case) -> str:
    s, po, inv = c.supplier, c.purchase_order, c.invoice
    out: list[str] = []

    out += ["SUPPLIER RECORD", f"  Name: {s.name}"]
    out += [f"  Also trades as: {', '.join(s.aliases)}"]
    out += [f"  VAT number: {s.vat_number}", f"  Bank account on file: ending {s.bank_account_last4}"]
    out += [f"  Contract pricing: {s.contract}", ""]

    out += [f"PURCHASE ORDER {po.po_number} (raised {_d(po.date)})"]
    for l in po.lines:
        out.append(f"  {l.sku:<14} {l.description:<48} qty {l.qty:>3} @ {fmt_money(l.unit_price_pence):>9}")
    out += [f"  Note: {n}" for n in po.notes] + [""]

    out.append("GOODS RECEIVED")
    for d in c.deliveries:
        items = ", ".join(f"{l.sku} x{l.qty}" for l in d.lines)
        out.append(f"  {d.grn_number} ({_d(d.date)}): {items}")
        out += [f"    Note: {n}" for n in d.notes]
    out.append("")

    out += [f"INVOICE {inv.invoice_number} (dated {_d(inv.date)})"]
    out += [f"  From: {inv.supplier_name}", f"  VAT number: {inv.supplier_vat_number or '(not shown)'}"]
    out += [f"  Pay to: account ending {inv.bank_account_last4}", f"  Your PO: {inv.po_number}"]
    out += _invoice_lines(inv.lines)
    net = sum(line_net_pence(l.qty, l.unit_price_pence) for l in inv.lines)
    out.append(f"  Net: {fmt_money(net)}   VAT: {fmt_money(inv.vat_total_pence)}")
    for a in inv.credits_applied:
        out.append(f"  Less credit {a.credit_note_number}: {fmt_money(a.amount_pence)}")
    out.append(f"  Total due: {fmt_money(inv.total_due_pence)}")
    out += [f"  Note: {n}" for n in inv.notes] + [""]

    out.append("PREVIOUS INVOICES FROM THIS SUPPLIER")
    if not c.prior_invoices:
        out.append("  (none)")
    for p in sorted(c.prior_invoices, key=lambda p: p.date):
        out.append(f"  {p.invoice_number} ({_d(p.date)}), PO {p.po_number}, total {fmt_money(p.total_due_pence)}, {p.status}")
        out += ["  " + line for line in _invoice_lines(p.lines)]
    out.append("")

    out.append("OPEN CREDIT NOTES FROM THIS SUPPLIER")
    if not c.open_credit_notes:
        out.append("  (none)")
    for cn in c.open_credit_notes:
        out.append(f"  {cn.credit_note_number} ({_d(cn.date)}), {fmt_money(cn.amount_pence)}, PO {cn.po_number}: {cn.reason}")

    return "\n".join(out)
