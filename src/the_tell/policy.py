"""The accounts payable policy. The model is given POLICY_TEXT; the oracle uses the constants.

If you change a rule here, change it in both places. tests/test_generate.py checks the
VAT table in the catalogue matches the categories described below.
"""

from the_tell.domain import Label

BUYER = "Kettleworth Cafés Ltd"

PRICE_TOLERANCE_PCT = {"variable": 2, "fixed": 0}

# When more than one problem applies, the first in this list wins.
PRECEDENCE = [
    Label.SUPPLIER_MISMATCH,
    Label.DUPLICATE,
    Label.QUANTITY_VARIANCE,
    Label.PRICE_VARIANCE,
    Label.TAX_ERROR,
    Label.UNAPPLIED_CREDIT,
]

POLICY_TEXT = f"""\
ACCOUNTS PAYABLE POLICY: {BUYER}, supplier invoice review

Choose exactly one outcome for each invoice.

APPROVE
  None of the problems below applies.

SUPPLIER_MISMATCH
  The VAT number on the invoice is missing or does not match the supplier record, or the
  bank account on the invoice differs from the account on the supplier record.
  Trading names listed on the supplier record are acceptable. A name alone never proves
  identity; the VAT number does. Any change of bank details must be verified by phone
  before payment, so an invoice showing new bank details is always held.

DUPLICATE
  The invoice is an exact repeat of an invoice already received on the same purchase
  order (same items, quantities and prices), whatever its invoice number or date.
  Standing orders billed against different purchase orders are not duplicates.

QUANTITY_VARIANCE
  Across all invoices on the purchase order, including this one, the quantity invoiced for
  any item exceeds the quantity delivered according to the goods received notes.
  This includes an invoice that bills goods already invoiced together with newly delivered
  goods, for example a full invoice after a part invoice. That is not a DUPLICATE, because
  it is not an exact repeat.

PRICE_VARIANCE
  A unit price is higher than the purchase order price by more than the tolerance.
  Tolerance: 2% for suppliers on variable-price contracts, 0% for fixed-price contracts.
  A price change noted on the purchase order as agreed with the supplier replaces the PO
  price from its effective date, provided the invoice is dated on or after that date.
  The note on the purchase order is the record of the agreement; no other evidence is needed.
  The tolerance then applies to the agreed price. Lower prices are always acceptable.

TAX_ERROR
  Any line is charged at the wrong VAT rate, or the VAT total does not equal the sum of
  the VAT on each line. VAT rates:
    - Tea, coffee, milk and cream: 0%
    - Biscuits, cakes and scones: 0%, except biscuits wholly or partly covered in
      chocolate: 20%
    - Crisps, confectionery, bottled water and soft drinks: 20%
    - Packaging, equipment and services: 20%

UNAPPLIED_CREDIT
  An open credit note from the supplier that references this purchase order has not been
  deducted in full on this invoice. Credit notes are always deducted from the next invoice
  on the same purchase order, even if the supplier says the credit will be refunded
  separately. Credit notes that reference a different purchase order are not deducted.

If more than one problem applies, choose the first in this order:
  {", ".join(PRECEDENCE)}
"""
