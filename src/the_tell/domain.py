"""The data model: what one invoice case looks like.

Money is always stored as whole pence (int), never as floats, so sums are exact.
"""

import datetime as dt
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel


class Label(StrEnum):
    """The one decision the model makes for each invoice."""

    APPROVE = "APPROVE"
    SUPPLIER_MISMATCH = "SUPPLIER_MISMATCH"
    DUPLICATE = "DUPLICATE"
    QUANTITY_VARIANCE = "QUANTITY_VARIANCE"
    PRICE_VARIANCE = "PRICE_VARIANCE"
    TAX_ERROR = "TAX_ERROR"
    UNAPPLIED_CREDIT = "UNAPPLIED_CREDIT"


class Supplier(BaseModel):
    supplier_id: str
    name: str
    aliases: list[str]  # trading names the supplier record accepts
    vat_number: str
    bank_account_last4: str
    contract: Literal["fixed", "variable"]  # fixed-price contracts have 0% price tolerance
    categories: list[str]  # which product categories they sell
    invoice_prefix: str


class POLine(BaseModel):
    sku: str
    description: str
    qty: int
    unit_price_pence: int


class PriceAgreement(BaseModel):
    """A written price change recorded on the PO. The model only sees it as a note."""

    uplift_pct: int
    effective: dt.date


class PurchaseOrder(BaseModel):
    po_number: str
    date: dt.date
    lines: list[POLine]
    price_agreements: list[PriceAgreement] = []
    notes: list[str] = []


class DeliveryLine(BaseModel):
    sku: str
    qty: int


class Delivery(BaseModel):
    grn_number: str  # goods received note
    date: dt.date
    lines: list[DeliveryLine]
    notes: list[str] = []


class InvoiceLine(BaseModel):
    sku: str
    description: str
    qty: int
    unit_price_pence: int
    vat_rate_pct: int


class CreditApplied(BaseModel):
    credit_note_number: str
    amount_pence: int


class Invoice(BaseModel):
    invoice_number: str
    date: dt.date
    supplier_name: str
    supplier_vat_number: str | None
    bank_account_last4: str
    po_number: str
    lines: list[InvoiceLine]
    credits_applied: list[CreditApplied] = []
    vat_total_pence: int = 0
    total_due_pence: int = 0
    notes: list[str] = []


class PriorInvoice(BaseModel):
    """An invoice from the same supplier already in the ledger."""

    invoice_number: str
    date: dt.date
    po_number: str
    lines: list[InvoiceLine]
    total_due_pence: int
    status: Literal["paid", "approved"]


class CreditNote(BaseModel):
    credit_note_number: str
    date: dt.date
    po_number: str  # the PO the credit must be deducted against
    amount_pence: int  # gross, deducted from the invoice total
    reason: str


class Case(BaseModel):
    case_id: str
    label: Label  # the correct decision, known because we built the case
    scenario: str  # which generator scenario made it
    difficulty: Literal["easy", "hard"]
    amount_at_risk_pence: int  # money lost if this invoice were wrongly approved
    supplier: Supplier
    purchase_order: PurchaseOrder
    deliveries: list[Delivery]
    invoice: Invoice
    prior_invoices: list[PriorInvoice]
    open_credit_notes: list[CreditNote]


# --- Money helpers. Shared by the generator and the oracle so both round the same way. ---


def line_net_pence(qty: int, unit_price_pence: int) -> int:
    return qty * unit_price_pence


def line_vat_pence(qty: int, unit_price_pence: int, vat_rate_pct: int) -> int:
    """VAT on one line, rounded half up to the nearest penny."""
    return (qty * unit_price_pence * vat_rate_pct + 50) // 100


def lines_vat_pence(lines: list[InvoiceLine]) -> int:
    return sum(line_vat_pence(l.qty, l.unit_price_pence, l.vat_rate_pct) for l in lines)


def lines_net_pence(lines: list[InvoiceLine]) -> int:
    return sum(line_net_pence(l.qty, l.unit_price_pence) for l in lines)


def uplifted_price_pence(price_pence: int, uplift_pct: int) -> int:
    """A price after an agreed percentage increase, rounded half up."""
    return (price_pence * (100 + uplift_pct) + 50) // 100


def fmt_money(pence: int) -> str:
    sign = "-" if pence < 0 else ""
    pence = abs(pence)
    return f"{sign}£{pence // 100:,}.{pence % 100:02d}"
