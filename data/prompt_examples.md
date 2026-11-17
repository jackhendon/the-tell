# What the model receives

Every case gets the same system prompt, followed by one user message with the
documents and the automated checks. Three examples follow, with the correct answer
shown above each (the model never sees it).

## System prompt (identical for every case)

```
You review supplier invoices for the accounts payable team at Kettleworth Cafés Ltd.
Apply the policy below exactly as written. The automated checks are correct arithmetic,
but they do not apply the policy: that is your job.

ACCOUNTS PAYABLE POLICY: Kettleworth Cafés Ltd, supplier invoice review

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
  SUPPLIER_MISMATCH, DUPLICATE, QUANTITY_VARIANCE, PRICE_VARIANCE, TAX_ERROR, UNAPPLIED_CREDIT

Reply with exactly two lines and nothing else:
OUTCOME: <one of APPROVE, SUPPLIER_MISMATCH, DUPLICATE, QUANTITY_VARIANCE, PRICE_VARIANCE, TAX_ERROR, UNAPPLIED_CREDIT>
CONFIDENCE: <a whole number from 0 to 100: the probability that your outcome is correct>

```

## case-00018: correct answer APPROVE (agreed_uplift)

```
SUPPLIER RECORD
  Name: Ingleby Foodservice Ltd
  Also trades as: Ingleby Foodservice
  VAT number: GB 261 4014 19
  Bank account on file: ending 3643
  Contract pricing: fixed

PURCHASE ORDER PO-2026-1838 (raised 2 Aug 2026)
  DRY-WHL-6      Whole milk 2L (case of 6)                        qty  34 @     £7.55
  TEA-EBT-1100   English breakfast tea bags (box of 1,100)        qty   7 @    £18.36
  SNK-CDG-12     Milk chocolate digestives 300g (case of 12)      qty   7 @    £12.43
  BAK-VSP-12     Victoria sponge, 12 slices                       qty   7 @    £17.39
  Note: Deliver to Market Street branch.
  Note: Supplier price review: 3% uplift agreed by Purchasing, applies from 4 August 2026.

GOODS RECEIVED
  GRN-43233 (4 Aug 2026): DRY-WHL-6 x34, TEA-EBT-1100 x7, SNK-CDG-12 x7, BAK-VSP-12 x7

INVOICE ING-68433 (dated 4 Aug 2026)
  From: Ingleby Foodservice Ltd
  VAT number: GB 261 4014 19
  Pay to: account ending 3643
  Your PO: PO-2026-1838
  DRY-WHL-6      Whole milk 2L (case of 6)                        qty  34 @     £7.78  VAT  0%  net    £264.52
  TEA-EBT-1100   English breakfast tea bags (box of 1,100)        qty   7 @    £18.91  VAT  0%  net    £132.37
  SNK-CDG-12     Milk chocolate digestives 300g (case of 12)      qty   7 @    £12.80  VAT 20%  net     £89.60
  BAK-VSP-12     Victoria sponge, 12 slices                       qty   7 @    £17.91  VAT  0%  net    £125.37
  Net: £611.86   VAT: £17.92
  Total due: £629.78

PREVIOUS INVOICES FROM THIS SUPPLIER
  ING-68129 (24 Apr 2026), PO PO-2026-1426, total £307.91, paid
    DRY-SSK-6      Semi-skimmed milk 2L (case of 6)                 qty  41 @     £7.51  VAT  0%  net    £307.91
  ING-68392 (21 Jul 2026), PO PO-2026-1759, total £308.56, paid
    TEA-EGL-500    Earl Grey loose leaf tea 500g                    qty   5 @    £15.85  VAT  0%  net     £79.25
    SNK-SPW-24     Sparkling spring water 500ml (case of 24)        qty   9 @     £9.81  VAT 20%  net     £88.29
    BAK-VSP-12     Victoria sponge, 12 slices                       qty   8 @    £15.42  VAT  0%  net    £123.36
  ING-68394 (22 Jul 2026), PO PO-2026-1763, total £416.64, paid
    DRY-SSK-6      Semi-skimmed milk 2L (case of 6)                 qty  56 @     £7.44  VAT  0%  net    £416.64

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)

AUTOMATED CHECKS (calculated by the AP system from the documents above)
  Supplier:
    Name on invoice matches: registered name
    VAT number on invoice: same as record
    Bank account on invoice: same as record
  Prices (invoice against purchase order):
    DRY-WHL-6      PO     £7.55  invoiced     £7.78  change +3.0%
    TEA-EBT-1100   PO    £18.36  invoiced    £18.91  change +3.0%
    SNK-CDG-12     PO    £12.43  invoiced    £12.80  change +3.0%
    BAK-VSP-12     PO    £17.39  invoiced    £17.91  change +3.0%
  Quantities on this PO:
    DRY-WHL-6      ordered  34  received  34  invoiced earlier   0  this invoice  34  total invoiced  34
    TEA-EBT-1100   ordered   7  received   7  invoiced earlier   0  this invoice   7  total invoiced   7
    SNK-CDG-12     ordered   7  received   7  invoiced earlier   0  this invoice   7  total invoiced   7
    BAK-VSP-12     ordered   7  received   7  invoiced earlier   0  this invoice   7  total invoiced   7
  Earlier invoices on this PO:
    (none)
  VAT:
    Sum of VAT on each line, at the rates charged: £17.92
    VAT total stated on invoice: £17.92
  Open credit notes referencing this PO:
    (none)

Decide the outcome for this invoice.
```

## case-00078: correct answer PRICE_VARIANCE (just_over)

```
SUPPLIER RECORD
  Name: Wexcombe Tea Merchants Ltd
  Also trades as: Wexcombe Tea Merchants, Wexcombe Tea
  VAT number: GB 993 5181 90
  Bank account on file: ending 3374
  Contract pricing: variable

PURCHASE ORDER PO-2026-2008 (raised 14 Sep 2026)
  COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   7 @    £24.40
  TEA-EGL-500    Earl Grey loose leaf tea 500g                    qty  11 @    £17.04
  COF-COL-1K     Colombian coffee beans 1kg                       qty   6 @    £21.13

GOODS RECEIVED
  GRN-60817 (15 Sep 2026): COF-DEC-1K x7, TEA-EGL-500 x11, COF-COL-1K x6
    Note: Delivered to rear entrance.

INVOICE WEX-12467 (dated 17 Sep 2026)
  From: Wexcombe Tea Merchants Ltd
  VAT number: GB 993 5181 90
  Pay to: account ending 3374
  Your PO: PO-2026-2008
  COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   7 @    £25.26  VAT  0%  net    £176.82
  TEA-EGL-500    Earl Grey loose leaf tea 500g                    qty  11 @    £17.04  VAT  0%  net    £187.44
  COF-COL-1K     Colombian coffee beans 1kg                       qty   6 @    £21.13  VAT  0%  net    £126.78
  Net: £491.04   VAT: £0.00
  Total due: £491.04
  Note: Goods remain our property until paid in full.

PREVIOUS INVOICES FROM THIS SUPPLIER
  WEX-12272 (14 Jul 2026), PO PO-2026-1744, total £322.98, paid
    COF-COL-1K     Colombian coffee beans 1kg                       qty   5 @    £21.84  VAT  0%  net    £109.20
    TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   4 @    £23.12  VAT  0%  net     £92.48
    COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   5 @    £24.26  VAT  0%  net    £121.30

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)

AUTOMATED CHECKS (calculated by the AP system from the documents above)
  Supplier:
    Name on invoice matches: registered name
    VAT number on invoice: same as record
    Bank account on invoice: same as record
  Prices (invoice against purchase order):
    COF-DEC-1K     PO    £24.40  invoiced    £25.26  change +3.5%
    TEA-EGL-500    PO    £17.04  invoiced    £17.04  change +0.0%
    COF-COL-1K     PO    £21.13  invoiced    £21.13  change +0.0%
  Quantities on this PO:
    COF-DEC-1K     ordered   7  received   7  invoiced earlier   0  this invoice   7  total invoiced   7
    TEA-EGL-500    ordered  11  received  11  invoiced earlier   0  this invoice  11  total invoiced  11
    COF-COL-1K     ordered   6  received   6  invoiced earlier   0  this invoice   6  total invoiced   6
  Earlier invoices on this PO:
    (none)
  VAT:
    Sum of VAT on each line, at the rates charged: £0.00
    VAT total stated on invoice: £0.00
  Open credit notes referencing this PO:
    (none)

Decide the outcome for this invoice.
```

## case-00015: correct answer UNAPPLIED_CREDIT (refund_separately)

```
SUPPLIER RECORD
  Name: Ingleby Foodservice Ltd
  Also trades as: Ingleby Foodservice
  VAT number: GB 261 4014 19
  Bank account on file: ending 3643
  Contract pricing: fixed

PURCHASE ORDER PO-2026-2110 (raised 9 Oct 2026)
  SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty   2 @    £14.63
  BAK-SCN-24     Fruit scones (tray of 24)                        qty  14 @    £15.04
  SNK-CRS-24     Sea salt crisps 40g (case of 24)                 qty   6 @    £11.49

GOODS RECEIVED
  GRN-86693 (14 Oct 2026): SNK-CSB-12 x2, BAK-SCN-24 x14, SNK-CRS-24 x6

INVOICE ING-68661 (dated 19 Oct 2026)
  From: Ingleby Foodservice Ltd
  VAT number: GB 261 4014 19
  Pay to: account ending 3643
  Your PO: PO-2026-2110
  SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty   2 @    £14.63  VAT 20%  net     £29.26
  BAK-SCN-24     Fruit scones (tray of 24)                        qty  14 @    £15.04  VAT  0%  net    £210.56
  SNK-CRS-24     Sea salt crisps 40g (case of 24)                 qty   6 @    £11.49  VAT 20%  net     £68.94
  Net: £308.76   VAT: £19.64
  Total due: £328.40
  Note: Please quote the invoice number on your remittance.
  Note: Credit CN-7946 is not included here and will be settled separately.

PREVIOUS INVOICES FROM THIS SUPPLIER
  ING-68506 (28 Aug 2026), PO PO-2026-1916, total £536.64, paid
    TEA-EGL-500    Earl Grey loose leaf tea 500g                    qty   8 @    £18.08  VAT  0%  net    £144.64
    DRY-SSK-6      Semi-skimmed milk 2L (case of 6)                 qty  49 @     £8.00  VAT  0%  net    £392.00

OPEN CREDIT NOTES FROM THIS SUPPLIER
  CN-7946 (17 Oct 2026), £72.88, PO PO-2026-2110: Goods on delivery GRN-86693 below specification. To be deducted from your next invoice against PO-2026-2110.

AUTOMATED CHECKS (calculated by the AP system from the documents above)
  Supplier:
    Name on invoice matches: registered name
    VAT number on invoice: same as record
    Bank account on invoice: same as record
  Prices (invoice against purchase order):
    SNK-CSB-12     PO    £14.63  invoiced    £14.63  change +0.0%
    BAK-SCN-24     PO    £15.04  invoiced    £15.04  change +0.0%
    SNK-CRS-24     PO    £11.49  invoiced    £11.49  change +0.0%
  Quantities on this PO:
    SNK-CSB-12     ordered   2  received   2  invoiced earlier   0  this invoice   2  total invoiced   2
    BAK-SCN-24     ordered  14  received  14  invoiced earlier   0  this invoice  14  total invoiced  14
    SNK-CRS-24     ordered   6  received   6  invoiced earlier   0  this invoice   6  total invoiced   6
  Earlier invoices on this PO:
    (none)
  VAT:
    Sum of VAT on each line, at the rates charged: £19.64
    VAT total stated on invoice: £19.64
  Open credit notes referencing this PO:
    CN-7946: £72.88, deducted on this invoice: £0.00

Decide the outcome for this invoice.
```
