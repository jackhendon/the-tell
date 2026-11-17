# Review sample

40 cases: one from each of the 30 scenarios, then random extras.
For each case, check two things and note anything off:

1. **Realism.** Would a real AP clerk see documents like this?
2. **Forced label.** Does the quoted policy rule force this answer, with no other
   sensible reading? This matters most. If a sensible reader could choose differently,
   the model's 'mistakes' on such cases measure an unclear policy, not judgement.

Cases marked **Possible disagreement** are where I think a reasonable person might
pause. Decide whether the policy wording settles it, or needs changing.

<details><summary>AP policy given to the model</summary>

```
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
  The invoice bills the same goods as an invoice already received on the same purchase
  order (same items, quantities and prices), whatever its invoice number or date.
  Standing orders billed against different purchase orders are not duplicates.

QUANTITY_VARIANCE
  Across all invoices on the purchase order, including this one, the quantity invoiced for
  any item exceeds the quantity delivered according to the goods received notes.

PRICE_VARIANCE
  A unit price is higher than the purchase order price by more than the tolerance.
  Tolerance: 2% for suppliers on variable-price contracts, 0% for fixed-price contracts.
  A price change agreed in writing and recorded on the purchase order replaces the PO
  price from its effective date, provided the invoice is dated on or after that date.
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

```
</details>

## 1. case-01091: APPROVE (agreed_uplift, hard)

Money at risk if wrongly approved: £0.00

Rule that decides it: PRICE_VARIANCE: an agreed change recorded on the PO replaces the PO price from its effective date.

**Possible disagreement:** Some clerks expect fixed-price contracts never to change. The policy wording allows it.

```
SUPPLIER RECORD
  Name: Millbeck Dairies Ltd
  Also trades as: Millbeck Dairies
  VAT number: GB 928 1590 13
  Bank account on file: ending 6164
  Contract pricing: fixed

PURCHASE ORDER PO-2026-2020 (raised 17 Sep 2026)
  DRY-SSK-6      Semi-skimmed milk 2L (case of 6)                 qty  18 @     £8.17
  DRY-CRM-1L     Double cream 1L                                  qty  29 @     £4.22
  DRY-WHL-6      Whole milk 2L (case of 6)                        qty  34 @     £8.20
  Note: Supplier price review: 6% uplift agreed by Purchasing, applies from 23 September 2026.

GOODS RECEIVED
  GRN-93687 (23 Sep 2026): DRY-SSK-6 x18, DRY-CRM-1L x29, DRY-WHL-6 x34

INVOICE MIL-31197 (dated 27 Sep 2026)
  From: Millbeck Dairies Ltd
  VAT number: GB 928 1590 13
  Pay to: account ending 6164
  Your PO: PO-2026-2020
  DRY-SSK-6      Semi-skimmed milk 2L (case of 6)                 qty  18 @     £8.66  VAT  0%  net    £155.88
  DRY-CRM-1L     Double cream 1L                                  qty  29 @     £4.47  VAT  0%  net    £129.63
  DRY-WHL-6      Whole milk 2L (case of 6)                        qty  34 @     £8.69  VAT  0%  net    £295.46
  Net: £580.97   VAT: £0.00
  Total due: £580.97

PREVIOUS INVOICES FROM THIS SUPPLIER
  MIL-30871 (11 Jun 2026), PO PO-2026-1613, total £308.49, paid
    DRY-WHL-6      Whole milk 2L (case of 6)                        qty  39 @     £7.91  VAT  0%  net    £308.49
  MIL-30914 (25 Jun 2026), PO PO-2026-1679, total £110.76, paid
    DRY-WHL-6      Whole milk 2L (case of 6)                        qty  13 @     £8.52  VAT  0%  net    £110.76
  MIL-31130 (5 Sep 2026), PO PO-2026-1957, total £118.58, paid
    DRY-WHL-6      Whole milk 2L (case of 6)                        qty  14 @     £8.47  VAT  0%  net    £118.58

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 2. case-01225: TAX_ERROR (standard_on_zero_rated, easy)

Money at risk if wrongly approved: £87.44

Rule that decides it: TAX_ERROR: tea, coffee, milk and cream are 0%.

```
SUPPLIER RECORD
  Name: Calder Wholesale Ltd
  Also trades as: Calder Wholesale
  VAT number: GB 154 7280 38
  Bank account on file: ending 5926
  Contract pricing: fixed

PURCHASE ORDER PO-2026-2063 (raised 27 Sep 2026)
  DRY-SSK-6      Semi-skimmed milk 2L (case of 6)                 qty  59 @     £7.41
  COF-COL-1K     Colombian coffee beans 1kg                       qty   5 @    £23.67
  Note: Deliver before 8am.

GOODS RECEIVED
  GRN-39386 (30 Sep 2026): DRY-SSK-6 x59, COF-COL-1K x5

INVOICE CAL-34614 (dated 3 Oct 2026)
  From: Calder Wholesale Ltd
  VAT number: GB 154 7280 38
  Pay to: account ending 5926
  Your PO: PO-2026-2063
  DRY-SSK-6      Semi-skimmed milk 2L (case of 6)                 qty  59 @     £7.41  VAT 20%  net    £437.19
  COF-COL-1K     Colombian coffee beans 1kg                       qty   5 @    £23.67  VAT  0%  net    £118.35
  Net: £555.54   VAT: £87.44
  Total due: £642.98
  Note: Please quote the invoice number on your remittance.

PREVIOUS INVOICES FROM THIS SUPPLIER
  (none)

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 3. case-00081: UNAPPLIED_CREDIT (partly_applied, hard)

Money at risk if wrongly approved: £11.61

Rule that decides it: UNAPPLIED_CREDIT: must be deducted in full.

```
SUPPLIER RECORD
  Name: Langdon Tea Company Ltd
  Also trades as: Langdon Tea Company, Langdon Tea
  VAT number: GB 116 3726 51
  Bank account on file: ending 6485
  Contract pricing: variable

PURCHASE ORDER PO-2026-1597 (raised 3 Jun 2026)
  TEA-EBT-1100   English breakfast tea bags (box of 1,100)        qty   5 @    £17.57
  COF-COL-1K     Colombian coffee beans 1kg                       qty   4 @    £21.61
  TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   5 @    £23.40

GOODS RECEIVED
  GRN-67229 (6 Jun 2026): TEA-EBT-1100 x5, COF-COL-1K x4, TEA-ASM-1K x5

INVOICE LAN-42758 (dated 6 Jun 2026)
  From: Langdon Tea Company Ltd
  VAT number: GB 116 3726 51
  Pay to: account ending 6485
  Your PO: PO-2026-1597
  TEA-EBT-1100   English breakfast tea bags (box of 1,100)        qty   5 @    £17.57  VAT  0%  net     £87.85
  COF-COL-1K     Colombian coffee beans 1kg                       qty   4 @    £21.61  VAT  0%  net     £86.44
  TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   5 @    £23.40  VAT  0%  net    £117.00
  Net: £291.29   VAT: £0.00
  Less credit CN-4161: £11.61
  Total due: £279.68
  Note: Payment terms: 30 days from invoice date.
  Note: Less credit note CN-4161.

PREVIOUS INVOICES FROM THIS SUPPLIER
  (none)

OPEN CREDIT NOTES FROM THIS SUPPLIER
  CN-4161 (1 Jun 2026), £23.22, PO PO-2026-1597: Items missing from previous delivery. To be deducted from your next invoice against PO-2026-1597.
```

Your notes:

## 4. case-01787: QUANTITY_VARIANCE (overbilled, easy)

Money at risk if wrongly approved: £31.78

Rule that decides it: QUANTITY_VARIANCE: invoiced exceeds delivered.

```
SUPPLIER RECORD
  Name: Oakhurst Tea Company Ltd
  Also trades as: Oakhurst Tea Company, Oakhurst Tea
  VAT number: GB 326 5020 14
  Bank account on file: ending 7057
  Contract pricing: fixed

PURCHASE ORDER PO-2026-2120 (raised 12 Oct 2026)
  TEA-EBT-1100   English breakfast tea bags (box of 1,100)        qty  12 @    £19.94
  TEA-EGL-500    Earl Grey loose leaf tea 500g                    qty   4 @    £15.89
  TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   6 @    £24.76
  COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty  11 @    £23.90

GOODS RECEIVED
  GRN-81633 (17 Oct 2026): TEA-EBT-1100 x12, TEA-EGL-500 x4, TEA-ASM-1K x6, COF-DEC-1K x11
    Note: Left with front-of-house staff.

INVOICE OAK-77156 (dated 17 Oct 2026)
  From: Oakhurst Tea Company Ltd
  VAT number: GB 326 5020 14
  Pay to: account ending 7057
  Your PO: PO-2026-2120
  TEA-EBT-1100   English breakfast tea bags (box of 1,100)        qty  12 @    £19.94  VAT  0%  net    £239.28
  TEA-EGL-500    Earl Grey loose leaf tea 500g                    qty   6 @    £15.89  VAT  0%  net     £95.34
  TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   6 @    £24.76  VAT  0%  net    £148.56
  COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty  11 @    £23.90  VAT  0%  net    £262.90
  Net: £746.08   VAT: £0.00
  Total due: £746.08

PREVIOUS INVOICES FROM THIS SUPPLIER
  (none)

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 5. case-00129: SUPPLIER_MISMATCH (bank_change, hard)

Money at risk if wrongly approved: £876.53

Rule that decides it: SUPPLIER_MISMATCH: new bank details are always held for phone verification.

```
SUPPLIER RECORD
  Name: Farleigh Dairies Ltd
  Also trades as: Farleigh Dairies
  VAT number: GB 304 3483 95
  Bank account on file: ending 4249
  Contract pricing: variable

PURCHASE ORDER PO-2026-1925 (raised 24 Aug 2026)
  DRY-WHL-6      Whole milk 2L (case of 6)                        qty  59 @     £7.75
  DRY-SSK-6      Semi-skimmed milk 2L (case of 6)                 qty  41 @     £8.08
  DRY-CRM-1L     Double cream 1L                                  qty  22 @     £4.00

GOODS RECEIVED
  GRN-75879 (25 Aug 2026): DRY-WHL-6 x59, DRY-SSK-6 x41, DRY-CRM-1L x22

INVOICE FAR-48112 (dated 30 Aug 2026)
  From: Farleigh Dairies Ltd
  VAT number: GB 304 3483 95
  Pay to: account ending 6701
  Your PO: PO-2026-1925
  DRY-WHL-6      Whole milk 2L (case of 6)                        qty  59 @     £7.75  VAT  0%  net    £457.25
  DRY-SSK-6      Semi-skimmed milk 2L (case of 6)                 qty  41 @     £8.08  VAT  0%  net    £331.28
  DRY-CRM-1L     Double cream 1L                                  qty  22 @     £4.00  VAT  0%  net     £88.00
  Net: £876.53   VAT: £0.00
  Total due: £876.53
  Note: Please note our bank details have changed. New account ending 6701. Kindly update your records.

PREVIOUS INVOICES FROM THIS SUPPLIER
  (none)

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 6. case-01040: APPROVE (clean, easy)

Money at risk if wrongly approved: £0.00

Rule that decides it: Nothing in the policy applies.

```
SUPPLIER RECORD
  Name: Ingleby Foodservice Ltd
  Also trades as: Ingleby Foodservice
  VAT number: GB 261 4014 19
  Bank account on file: ending 3643
  Contract pricing: fixed

PURCHASE ORDER PO-2026-2075 (raised 30 Sep 2026)
  DRY-CRM-1L     Double cream 1L                                  qty  58 @     £4.37
  SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty   4 @    £14.71

GOODS RECEIVED
  GRN-16499 (4 Oct 2026): DRY-CRM-1L x58, SNK-CSB-12 x4

INVOICE ING-68630 (dated 8 Oct 2026)
  From: Ingleby Foodservice Ltd
  VAT number: GB 261 4014 19
  Pay to: account ending 3643
  Your PO: PO-2026-2075
  DRY-CRM-1L     Double cream 1L                                  qty  58 @     £4.37  VAT  0%  net    £253.46
  SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty   4 @    £14.71  VAT 20%  net     £58.84
  Net: £312.30   VAT: £11.77
  Total due: £324.07

PREVIOUS INVOICES FROM THIS SUPPLIER
  ING-68433 (4 Aug 2026), PO PO-2026-1814, total £375.49, paid
    COF-COL-1K     Colombian coffee beans 1kg                       qty  10 @    £22.14  VAT  0%  net    £221.40
    SNK-SPW-24     Sparkling spring water 500ml (case of 24)        qty   7 @    £10.07  VAT 20%  net     £70.49
    SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty   4 @    £14.48  VAT 20%  net     £57.92

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 7. case-01163: TAX_ERROR (standard_on_zero_rated, easy)

Money at risk if wrongly approved: £21.60

Rule that decides it: TAX_ERROR: tea, coffee, milk and cream are 0%.

```
SUPPLIER RECORD
  Name: Wexcombe Tea Merchants Ltd
  Also trades as: Wexcombe Tea Merchants, Wexcombe Tea
  VAT number: GB 993 5181 90
  Bank account on file: ending 3374
  Contract pricing: variable

PURCHASE ORDER PO-2026-1802 (raised 24 Jul 2026)
  TEA-EBT-1100   English breakfast tea bags (box of 1,100)        qty   6 @    £18.00
  TEA-EGL-500    Earl Grey loose leaf tea 500g                    qty   4 @    £16.92

GOODS RECEIVED
  GRN-12714 (30 Jul 2026): TEA-EBT-1100 x6, TEA-EGL-500 x4

INVOICE WEX-12320 (dated 30 Jul 2026)
  From: Wexcombe Tea Merchants Ltd
  VAT number: GB 993 5181 90
  Pay to: account ending 3374
  Your PO: PO-2026-1802
  TEA-EBT-1100   English breakfast tea bags (box of 1,100)        qty   6 @    £18.00  VAT 20%  net    £108.00
  TEA-EGL-500    Earl Grey loose leaf tea 500g                    qty   4 @    £16.92  VAT  0%  net     £67.68
  Net: £175.68   VAT: £21.60
  Total due: £197.28

PREVIOUS INVOICES FROM THIS SUPPLIER
  WEX-12067 (7 May 2026), PO PO-2026-1469, total £40.34, paid
    TEA-EBT-1100   English breakfast tea bags (box of 1,100)        qty   2 @    £20.17  VAT  0%  net     £40.34
  WEX-12233 (1 Jul 2026), PO PO-2026-1690, total £310.06, paid
    TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   6 @    £25.99  VAT  0%  net    £155.94
    COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   3 @    £26.72  VAT  0%  net     £80.16
    TEA-EBT-1100   English breakfast tea bags (box of 1,100)        qty   4 @    £18.49  VAT  0%  net     £73.96
  WEX-12249 (7 Jul 2026), PO PO-2026-1710, total £117.00, paid
    TEA-EGL-500    Earl Grey loose leaf tea 500g                    qty   3 @    £16.10  VAT  0%  net     £48.30
    TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   3 @    £22.90  VAT  0%  net     £68.70

OPEN CREDIT NOTES FROM THIS SUPPLIER
  CN-4608 (12 Jul 2026), £26.29, PO PO-2026-1710: Items missing from previous delivery. To be deducted from your next invoice against PO-2026-1710.
```

Your notes:

## 8. case-00646: TAX_ERROR (standard_on_zero_rated, easy)

Money at risk if wrongly approved: £37.26

Rule that decides it: TAX_ERROR: tea, coffee, milk and cream are 0%.

```
SUPPLIER RECORD
  Name: Millbeck Dairies Ltd
  Also trades as: Millbeck Dairies
  VAT number: GB 928 1590 13
  Bank account on file: ending 6164
  Contract pricing: fixed

PURCHASE ORDER PO-2026-1923 (raised 23 Aug 2026)
  DRY-CRM-1L     Double cream 1L                                  qty  45 @     £4.14
  DRY-WHL-6      Whole milk 2L (case of 6)                        qty  45 @     £7.73
  DRY-SSK-6      Semi-skimmed milk 2L (case of 6)                 qty  43 @     £7.77

GOODS RECEIVED
  GRN-25255 (26 Aug 2026): DRY-CRM-1L x45, DRY-WHL-6 x45, DRY-SSK-6 x43

INVOICE MIL-31108 (dated 29 Aug 2026)
  From: Millbeck Dairies Ltd
  VAT number: GB 928 1590 13
  Pay to: account ending 6164
  Your PO: PO-2026-1923
  DRY-CRM-1L     Double cream 1L                                  qty  45 @     £4.14  VAT 20%  net    £186.30
  DRY-WHL-6      Whole milk 2L (case of 6)                        qty  45 @     £7.73  VAT  0%  net    £347.85
  DRY-SSK-6      Semi-skimmed milk 2L (case of 6)                 qty  43 @     £7.77  VAT  0%  net    £334.11
  Net: £868.26   VAT: £37.26
  Total due: £905.52

PREVIOUS INVOICES FROM THIS SUPPLIER
  (none)

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 9. case-00878: APPROVE (trading_name, hard)

Money at risk if wrongly approved: £0.00

Rule that decides it: SUPPLIER_MISMATCH: listed trading names are acceptable; the VAT number proves identity.

```
SUPPLIER RECORD
  Name: Penrith Vale Tea Merchants Ltd
  Also trades as: Penrith Vale Tea Merchants, Penrith Vale Tea
  VAT number: GB 079 2440 26
  Bank account on file: ending 8758
  Contract pricing: variable

PURCHASE ORDER PO-2026-2106 (raised 8 Oct 2026)
  TEA-EBT-1100   English breakfast tea bags (box of 1,100)        qty   8 @    £19.28
  COF-COL-1K     Colombian coffee beans 1kg                       qty   3 @    £24.70
  COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   7 @    £26.72
  TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   5 @    £26.22

GOODS RECEIVED
  GRN-70150 (13 Oct 2026): TEA-EBT-1100 x8, COF-COL-1K x3, COF-DEC-1K x7, TEA-ASM-1K x5

INVOICE PEN-26148 (dated 14 Oct 2026)
  From: Penrith Vale Tea Merchants
  VAT number: GB 079 2440 26
  Pay to: account ending 8758
  Your PO: PO-2026-2106
  TEA-EBT-1100   English breakfast tea bags (box of 1,100)        qty   8 @    £19.28  VAT  0%  net    £154.24
  COF-COL-1K     Colombian coffee beans 1kg                       qty   3 @    £24.70  VAT  0%  net     £74.10
  COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   7 @    £26.72  VAT  0%  net    £187.04
  TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   5 @    £26.22  VAT  0%  net    £131.10
  Net: £546.48   VAT: £0.00
  Total due: £546.48

PREVIOUS INVOICES FROM THIS SUPPLIER
  PEN-25834 (2 Jul 2026), PO PO-2026-1707, total £340.26, paid
    COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   7 @    £27.15  VAT  0%  net    £190.05
    TEA-EGL-500    Earl Grey loose leaf tea 500g                    qty   9 @    £16.69  VAT  0%  net    £150.21
  PEN-25863 (11 Jul 2026), PO PO-2026-1717, total £401.04, paid
    TEA-ASM-1K     Assam loose leaf tea 1kg                         qty  10 @    £25.48  VAT  0%  net    £254.80
    TEA-EBT-1100   English breakfast tea bags (box of 1,100)        qty   8 @    £18.28  VAT  0%  net    £146.24
  PEN-25954 (11 Aug 2026), PO PO-2026-1845, total £482.14, paid
    COF-COL-1K     Colombian coffee beans 1kg                       qty  11 @    £21.29  VAT  0%  net    £234.19
    TEA-EBT-1100   English breakfast tea bags (box of 1,100)        qty   7 @    £20.41  VAT  0%  net    £142.87
    TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   4 @    £26.27  VAT  0%  net    £105.08

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 10. case-01109: QUANTITY_VARIANCE (rebilled_first_delivery, hard)

Money at risk if wrongly approved: £469.53

Rule that decides it: QUANTITY_VARIANCE: across all invoices on the PO, invoiced exceeds delivered.

**Possible disagreement:** Part of this bill repeats an earlier invoice, so a clerk might call it a DUPLICATE. The policy defines DUPLICATE as the same items, quantities and prices, which this is not.

```
SUPPLIER RECORD
  Name: Elstow Catering Disposables Ltd
  Also trades as: Elstow Catering Disposables, Elstow Catering
  VAT number: GB 114 7104 97
  Bank account on file: ending 4662
  Contract pricing: variable

PURCHASE ORDER PO-2026-2018 (raised 16 Sep 2026)
  PKG-NAP-5000   Paper napkins (case of 5,000)                    qty   5 @    £26.21
  PKG-LID-1000   Sip lids for 12oz cups (case of 1,000)           qty   4 @    £33.24
  PKG-CUP-1000   12oz takeaway cups (case of 1,000)               qty   4 @    £62.24

GOODS RECEIVED
  GRN-36087 (18 Sep 2026): PKG-NAP-5000 x4, PKG-LID-1000 x3, PKG-CUP-1000 x3
    Note: Partial shipment. Outstanding quantity to follow.
  GRN-22241 (25 Sep 2026): PKG-NAP-5000 x1, PKG-LID-1000 x1, PKG-CUP-1000 x1

INVOICE ELS-19291 (dated 25 Sep 2026)
  From: Elstow Catering Disposables Ltd
  VAT number: GB 114 7104 97
  Pay to: account ending 4662
  Your PO: PO-2026-2018
  PKG-NAP-5000   Paper napkins (case of 5,000)                    qty   5 @    £26.21  VAT 20%  net    £131.05
  PKG-LID-1000   Sip lids for 12oz cups (case of 1,000)           qty   4 @    £33.24  VAT 20%  net    £132.96
  PKG-CUP-1000   12oz takeaway cups (case of 1,000)               qty   4 @    £62.24  VAT 20%  net    £248.96
  Net: £512.97   VAT: £102.59
  Total due: £615.56

PREVIOUS INVOICES FROM THIS SUPPLIER
  ELS-19013 (25 Jun 2026), PO PO-2026-1668, total £154.18, paid
    PKG-LID-1000   Sip lids for 12oz cups (case of 1,000)           qty   4 @    £32.12  VAT 20%  net    £128.48
  ELS-19164 (14 Aug 2026), PO PO-2026-1870, total £195.66, paid
    PKG-LID-1000   Sip lids for 12oz cups (case of 1,000)           qty   5 @    £32.61  VAT 20%  net    £163.05
  ELS-19271 (19 Sep 2026), PO PO-2026-2018, total £469.53, paid
    PKG-NAP-5000   Paper napkins (case of 5,000)                    qty   4 @    £26.21  VAT 20%  net    £104.84
    PKG-LID-1000   Sip lids for 12oz cups (case of 1,000)           qty   3 @    £33.24  VAT 20%  net     £99.72
    PKG-CUP-1000   12oz takeaway cups (case of 1,000)               qty   3 @    £62.24  VAT 20%  net    £186.72

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 11. case-00761: UNAPPLIED_CREDIT (refund_separately, hard)

Money at risk if wrongly approved: £42.92

Rule that decides it: UNAPPLIED_CREDIT: deducted even if the supplier says it will be refunded separately.

```
SUPPLIER RECORD
  Name: Aldwick Wholesale Ltd
  Also trades as: Aldwick Wholesale
  VAT number: GB 729 0222 79
  Bank account on file: ending 1971
  Contract pricing: variable

PURCHASE ORDER PO-2026-1675 (raised 22 Jun 2026)
  BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty   8 @    £10.72
  DRY-CRM-1L     Double cream 1L                                  qty  26 @     £4.53
  SNK-CDG-12     Milk chocolate digestives 300g (case of 12)      qty   8 @    £13.45
  TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   7 @    £26.40

GOODS RECEIVED
  GRN-26222 (23 Jun 2026): BAK-DIG-12 x8, DRY-CRM-1L x26, SNK-CDG-12 x8, TEA-ASM-1K x7
    Note: Delivered to rear entrance.

INVOICE ALD-51313 (dated 25 Jun 2026)
  From: Aldwick Wholesale Ltd
  VAT number: GB 729 0222 79
  Pay to: account ending 1971
  Your PO: PO-2026-1675
  BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty   8 @    £10.72  VAT  0%  net     £85.76
  DRY-CRM-1L     Double cream 1L                                  qty  26 @     £4.53  VAT  0%  net    £117.78
  SNK-CDG-12     Milk chocolate digestives 300g (case of 12)      qty   8 @    £13.45  VAT 20%  net    £107.60
  TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   7 @    £26.40  VAT  0%  net    £184.80
  Net: £495.94   VAT: £21.52
  Total due: £517.46
  Note: Goods remain our property until paid in full.
  Note: Credit CN-5065 is not included here and will be settled separately.

PREVIOUS INVOICES FROM THIS SUPPLIER
  (none)

OPEN CREDIT NOTES FROM THIS SUPPLIER
  CN-5065 (30 May 2026), £42.92, PO PO-2026-1675: Pricing error on previous invoice. To be deducted from your next invoice against PO-2026-1675.
```

Your notes:

## 12. case-00858: APPROVE (mixed_vat, hard)

Money at risk if wrongly approved: £0.00

Rule that decides it: TAX_ERROR: VAT table, chocolate-covered biscuits 20%, plain biscuits 0%.

```
SUPPLIER RECORD
  Name: Aldwick Wholesale Ltd
  Also trades as: Aldwick Wholesale
  VAT number: GB 729 0222 79
  Bank account on file: ending 1971
  Contract pricing: variable

PURCHASE ORDER PO-2026-1993 (raised 10 Sep 2026)
  TEA-ASM-1K     Assam loose leaf tea 1kg                         qty  10 @    £25.45
  COF-COL-1K     Colombian coffee beans 1kg                       qty  12 @    £21.69
  SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty   8 @    £16.13
  BAK-SHB-12     All-butter shortbread fingers 150g (case of 12)  qty   5 @    £14.65

GOODS RECEIVED
  GRN-73233 (12 Sep 2026): TEA-ASM-1K x10, COF-COL-1K x12, SNK-CSB-12 x8, BAK-SHB-12 x5
    Note: Left with front-of-house staff.

INVOICE ALD-51551 (dated 12 Sep 2026)
  From: Aldwick Wholesale Ltd
  VAT number: GB 729 0222 79
  Pay to: account ending 1971
  Your PO: PO-2026-1993
  TEA-ASM-1K     Assam loose leaf tea 1kg                         qty  10 @    £25.45  VAT  0%  net    £254.50
  COF-COL-1K     Colombian coffee beans 1kg                       qty  12 @    £21.69  VAT  0%  net    £260.28
  SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty   8 @    £16.13  VAT 20%  net    £129.04
  BAK-SHB-12     All-butter shortbread fingers 150g (case of 12)  qty   5 @    £14.65  VAT  0%  net     £73.25
  Net: £717.07   VAT: £25.81
  Total due: £742.88
  Note: Goods remain our property until paid in full.

PREVIOUS INVOICES FROM THIS SUPPLIER
  ALD-51516 (31 Aug 2026), PO PO-2026-1932, total £531.08, paid
    DRY-WHL-6      Whole milk 2L (case of 6)                        qty  41 @     £8.00  VAT  0%  net    £328.00
    TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   4 @    £26.24  VAT  0%  net    £104.96
    COF-COL-1K     Colombian coffee beans 1kg                       qty   4 @    £24.53  VAT  0%  net     £98.12

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 13. case-00281: DUPLICATE (new_number, hard)

Money at risk if wrongly approved: £586.96

Rule that decides it: DUPLICATE: same goods on the same PO, whatever the invoice number.

```
SUPPLIER RECORD
  Name: Stanwick Bakery Supplies Ltd
  Also trades as: Stanwick Bakery Supplies, Stanwick Bakery
  VAT number: GB 878 0175 98
  Bank account on file: ending 9930
  Contract pricing: variable

PURCHASE ORDER PO-2026-1735 (raised 7 Jul 2026)
  SNK-CDG-12     Milk chocolate digestives 300g (case of 12)      qty  12 @    £12.99
  BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty  15 @    £10.99
  BAK-VSP-12     Victoria sponge, 12 slices                       qty  15 @    £15.67

GOODS RECEIVED
  GRN-97609 (9 Jul 2026): SNK-CDG-12 x12, BAK-DIG-12 x15, BAK-VSP-12 x15

INVOICE STA-54763 (dated 11 Jul 2026)
  From: Stanwick Bakery Supplies Ltd
  VAT number: GB 878 0175 98
  Pay to: account ending 9930
  Your PO: PO-2026-1735
  SNK-CDG-12     Milk chocolate digestives 300g (case of 12)      qty  12 @    £12.99  VAT 20%  net    £155.88
  BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty  15 @    £10.99  VAT  0%  net    £164.85
  BAK-VSP-12     Victoria sponge, 12 slices                       qty  15 @    £15.67  VAT  0%  net    £235.05
  Net: £555.78   VAT: £31.18
  Total due: £586.96

PREVIOUS INVOICES FROM THIS SUPPLIER
  STA-54441 (26 Mar 2026), PO PO-2026-1309, total £278.10, paid
    BAK-SCN-24     Fruit scones (tray of 24)                        qty  10 @    £14.53  VAT  0%  net    £145.30
    BAK-SHB-12     All-butter shortbread fingers 150g (case of 12)  qty  10 @    £13.28  VAT  0%  net    £132.80
  STA-54730 (30 Jun 2026), PO PO-2026-1685, total £168.24, paid
    SNK-CDG-12     Milk chocolate digestives 300g (case of 12)      qty  10 @    £14.02  VAT 20%  net    £140.20
  STA-54739 (3 Jul 2026), PO PO-2026-1735, total £586.96, paid
    SNK-CDG-12     Milk chocolate digestives 300g (case of 12)      qty  12 @    £12.99  VAT 20%  net    £155.88
    BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty  15 @    £10.99  VAT  0%  net    £164.85
    BAK-VSP-12     Victoria sponge, 12 slices                       qty  15 @    £15.67  VAT  0%  net    £235.05

OPEN CREDIT NOTES FROM THIS SUPPLIER
  CN-4050 (8 Jul 2026), £108.81, PO PO-2026-1685: Items missing from previous delivery. To be deducted from your next invoice against PO-2026-1685.
```

Your notes:

## 14. case-00173: UNAPPLIED_CREDIT (credit_ignored, easy)

Money at risk if wrongly approved: £25.65

Rule that decides it: UNAPPLIED_CREDIT: open credit on this PO not deducted.

```
SUPPLIER RECORD
  Name: Thornbury Catering Disposables Ltd
  Also trades as: Thornbury Catering Disposables, Thornbury Catering
  VAT number: GB 888 7180 33
  Bank account on file: ending 4537
  Contract pricing: fixed

PURCHASE ORDER PO-2026-1657 (raised 18 Jun 2026)
  PKG-CUP-1000   12oz takeaway cups (case of 1,000)               qty   5 @    £64.05
  PKG-NAP-5000   Paper napkins (case of 5,000)                    qty   4 @    £25.67
  PKG-LID-1000   Sip lids for 12oz cups (case of 1,000)           qty   2 @    £30.10

GOODS RECEIVED
  GRN-90316 (19 Jun 2026): PKG-CUP-1000 x5, PKG-NAP-5000 x4, PKG-LID-1000 x2
    Note: Delivered to rear entrance.

INVOICE THO-53009 (dated 23 Jun 2026)
  From: Thornbury Catering Disposables Ltd
  VAT number: GB 888 7180 33
  Pay to: account ending 4537
  Your PO: PO-2026-1657
  PKG-CUP-1000   12oz takeaway cups (case of 1,000)               qty   5 @    £64.05  VAT 20%  net    £320.25
  PKG-NAP-5000   Paper napkins (case of 5,000)                    qty   4 @    £25.67  VAT 20%  net    £102.68
  PKG-LID-1000   Sip lids for 12oz cups (case of 1,000)           qty   2 @    £30.10  VAT 20%  net     £60.20
  Net: £483.13   VAT: £96.63
  Total due: £579.76

PREVIOUS INVOICES FROM THIS SUPPLIER
  THO-52810 (18 Apr 2026), PO PO-2026-1390, total £697.37, paid
    PKG-LID-1000   Sip lids for 12oz cups (case of 1,000)           qty   6 @    £31.28  VAT 20%  net    £187.68
    PKG-CUP-1000   12oz takeaway cups (case of 1,000)               qty   4 @    £65.94  VAT 20%  net    £263.76
    PKG-NAP-5000   Paper napkins (case of 5,000)                    qty   5 @    £25.94  VAT 20%  net    £129.70
  THO-52928 (27 May 2026), PO PO-2026-1548, total £286.70, paid
    PKG-CUP-1000   12oz takeaway cups (case of 1,000)               qty   4 @    £59.73  VAT 20%  net    £238.92
  THO-52951 (4 Jun 2026), PO PO-2026-1593, total £695.95, paid
    PKG-CUP-1000   12oz takeaway cups (case of 1,000)               qty   5 @    £67.33  VAT 20%  net    £336.65
    PKG-LID-1000   Sip lids for 12oz cups (case of 1,000)           qty   5 @    £32.00  VAT 20%  net    £160.00
    PKG-NAP-5000   Paper napkins (case of 5,000)                    qty   3 @    £27.77  VAT 20%  net     £83.31

OPEN CREDIT NOTES FROM THIS SUPPLIER
  CN-8958 (14 May 2026), £25.65, PO PO-2026-1657: Items missing from previous delivery. To be deducted from your next invoice against PO-2026-1657.
```

Your notes:

## 15. case-00507: APPROVE (price_within_tolerance, hard)

Money at risk if wrongly approved: £0.00

Rule that decides it: PRICE_VARIANCE: 2% tolerance on variable-price contracts.

```
SUPPLIER RECORD
  Name: Elstow Catering Disposables Ltd
  Also trades as: Elstow Catering Disposables, Elstow Catering
  VAT number: GB 114 7104 97
  Bank account on file: ending 4662
  Contract pricing: variable

PURCHASE ORDER PO-2026-1654 (raised 17 Jun 2026)
  PKG-LID-1000   Sip lids for 12oz cups (case of 1,000)           qty   4 @    £32.64
  PKG-NAP-5000   Paper napkins (case of 5,000)                    qty   6 @    £29.22
  PKG-CUP-1000   12oz takeaway cups (case of 1,000)               qty   4 @    £64.29

GOODS RECEIVED
  GRN-33240 (18 Jun 2026): PKG-LID-1000 x4, PKG-NAP-5000 x6, PKG-CUP-1000 x4

INVOICE ELS-19001 (dated 21 Jun 2026)
  From: Elstow Catering Disposables Ltd
  VAT number: GB 114 7104 97
  Pay to: account ending 4662
  Your PO: PO-2026-1654
  PKG-LID-1000   Sip lids for 12oz cups (case of 1,000)           qty   4 @    £32.64  VAT 20%  net    £130.56
  PKG-NAP-5000   Paper napkins (case of 5,000)                    qty   6 @    £29.44  VAT 20%  net    £176.64
  PKG-CUP-1000   12oz takeaway cups (case of 1,000)               qty   4 @    £64.29  VAT 20%  net    £257.16
  Net: £564.36   VAT: £112.87
  Total due: £677.23

PREVIOUS INVOICES FROM THIS SUPPLIER
  ELS-18631 (17 Feb 2026), PO PO-2026-1154, total £31.34, paid
    PKG-NAP-5000   Paper napkins (case of 5,000)                    qty   1 @    £26.12  VAT 20%  net     £26.12
  ELS-18805 (16 Apr 2026), PO PO-2026-1390, total £208.19, paid
    PKG-CUP-1000   12oz takeaway cups (case of 1,000)               qty   1 @    £61.37  VAT 20%  net     £61.37
    PKG-NAP-5000   Paper napkins (case of 5,000)                    qty   2 @    £26.22  VAT 20%  net     £52.44
    PKG-LID-1000   Sip lids for 12oz cups (case of 1,000)           qty   2 @    £29.84  VAT 20%  net     £59.68

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 16. case-01558: SUPPLIER_MISMATCH (lookalike_no_vat, hard)

Money at risk if wrongly approved: £160.53

Rule that decides it: SUPPLIER_MISMATCH: VAT number missing.

```
SUPPLIER RECORD
  Name: Marston Leaf & Bean Ltd
  Also trades as: Marston Leaf & Bean, Marston Leaf
  VAT number: GB 505 8770 65
  Bank account on file: ending 8477
  Contract pricing: variable

PURCHASE ORDER PO-2026-1679 (raised 23 Jun 2026)
  COF-COL-1K     Colombian coffee beans 1kg                       qty   3 @    £22.65
  TEA-EGL-500    Earl Grey loose leaf tea 500g                    qty   6 @    £15.43
  Note: Contact the duty manager on arrival.

GOODS RECEIVED
  GRN-13021 (26 Jun 2026): COF-COL-1K x3, TEA-EGL-500 x6
    Note: Left with front-of-house staff.

INVOICE MAR-63218 (dated 26 Jun 2026)
  From: Marston Leaf & Bean & Co Ltd
  VAT number: (not shown)
  Pay to: account ending 8477
  Your PO: PO-2026-1679
  COF-COL-1K     Colombian coffee beans 1kg                       qty   3 @    £22.65  VAT  0%  net     £67.95
  TEA-EGL-500    Earl Grey loose leaf tea 500g                    qty   6 @    £15.43  VAT  0%  net     £92.58
  Net: £160.53   VAT: £0.00
  Total due: £160.53
  Note: Please quote the invoice number on your remittance.

PREVIOUS INVOICES FROM THIS SUPPLIER
  (none)

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 17. case-00164: APPROVE (trading_name, hard)

Money at risk if wrongly approved: £0.00

Rule that decides it: SUPPLIER_MISMATCH: listed trading names are acceptable; the VAT number proves identity.

```
SUPPLIER RECORD
  Name: Millbeck Dairies Ltd
  Also trades as: Millbeck Dairies
  VAT number: GB 928 1590 13
  Bank account on file: ending 6164
  Contract pricing: fixed

PURCHASE ORDER PO-2026-1640 (raised 14 Jun 2026)
  DRY-CRM-1L     Double cream 1L                                  qty  45 @     £4.43
  DRY-SSK-6      Semi-skimmed milk 2L (case of 6)                 qty  59 @     £7.74
  DRY-WHL-6      Whole milk 2L (case of 6)                        qty  16 @     £8.09

GOODS RECEIVED
  GRN-52964 (16 Jun 2026): DRY-CRM-1L x45, DRY-SSK-6 x59, DRY-WHL-6 x16

INVOICE MIL-30892 (dated 18 Jun 2026)
  From: Millbeck Dairies
  VAT number: GB 928 1590 13
  Pay to: account ending 6164
  Your PO: PO-2026-1640
  DRY-CRM-1L     Double cream 1L                                  qty  45 @     £4.43  VAT  0%  net    £199.35
  DRY-SSK-6      Semi-skimmed milk 2L (case of 6)                 qty  59 @     £7.74  VAT  0%  net    £456.66
  DRY-WHL-6      Whole milk 2L (case of 6)                        qty  16 @     £8.09  VAT  0%  net    £129.44
  Net: £785.45   VAT: £0.00
  Total due: £785.45

PREVIOUS INVOICES FROM THIS SUPPLIER
  MIL-30638 (25 Mar 2026), PO PO-2026-1295, total £116.34, paid
    DRY-WHL-6      Whole milk 2L (case of 6)                        qty  14 @     £8.31  VAT  0%  net    £116.34

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 18. case-00117: APPROVE (credit_other_po, hard)

Money at risk if wrongly approved: £0.00

Rule that decides it: UNAPPLIED_CREDIT: credits referencing a different PO are not deducted.

```
SUPPLIER RECORD
  Name: Selby Foodservice Ltd
  Also trades as: Selby Foodservice
  VAT number: GB 122 2029 72
  Bank account on file: ending 9762
  Contract pricing: variable

PURCHASE ORDER PO-2026-1800 (raised 24 Jul 2026)
  SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty   9 @    £16.59
  BAK-SCN-24     Fruit scones (tray of 24)                        qty   5 @    £14.06

GOODS RECEIVED
  GRN-71411 (28 Jul 2026): SNK-CSB-12 x9, BAK-SCN-24 x5

INVOICE SEL-44613 (dated 28 Jul 2026)
  From: Selby Foodservice Ltd
  VAT number: GB 122 2029 72
  Pay to: account ending 9762
  Your PO: PO-2026-1800
  SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty   9 @    £16.59  VAT 20%  net    £149.31
  BAK-SCN-24     Fruit scones (tray of 24)                        qty   5 @    £14.06  VAT  0%  net     £70.30
  Net: £219.61   VAT: £29.86
  Total due: £249.47
  Note: Please quote the invoice number on your remittance.

PREVIOUS INVOICES FROM THIS SUPPLIER
  SEL-44526 (29 Jun 2026), PO PO-2026-1679, total £471.19, paid
    SNK-CDG-12     Milk chocolate digestives 300g (case of 12)      qty  12 @    £12.21  VAT 20%  net    £146.52
    SNK-CRS-24     Sea salt crisps 40g (case of 24)                 qty   9 @    £11.46  VAT 20%  net    £103.14
    BAK-SHB-12     All-butter shortbread fingers 150g (case of 12)  qty  12 @    £14.30  VAT  0%  net    £171.60

OPEN CREDIT NOTES FROM THIS SUPPLIER
  CN-1228 (16 Jul 2026), £41.94, PO PO-2026-1679: Pricing error on previous invoice. To be deducted from your next invoice against PO-2026-1679.
```

Your notes:

## 19. case-01236: PRICE_VARIANCE (big_increase, easy)

Money at risk if wrongly approved: £13.02

Rule that decides it: PRICE_VARIANCE: above tolerance.

```
SUPPLIER RECORD
  Name: Quarrendon Bakery Supplies Ltd
  Also trades as: Quarrendon Bakery Supplies, Quarrendon Bakery
  VAT number: GB 240 2344 83
  Bank account on file: ending 4750
  Contract pricing: variable

PURCHASE ORDER PO-2026-2009 (raised 14 Sep 2026)
  BAK-VSP-12     Victoria sponge, 12 slices                       qty   5 @    £16.15
  BAK-SHB-12     All-butter shortbread fingers 150g (case of 12)  qty   6 @    £12.98
  BAK-SCN-24     Fruit scones (tray of 24)                        qty  10 @    £13.32
  BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty   4 @    £12.06

GOODS RECEIVED
  GRN-50570 (17 Sep 2026): BAK-VSP-12 x5, BAK-SHB-12 x6, BAK-SCN-24 x10, BAK-DIG-12 x4
    Note: Delivered to rear entrance.

INVOICE QUA-71971 (dated 19 Sep 2026)
  From: Quarrendon Bakery Supplies Ltd
  VAT number: GB 240 2344 83
  Pay to: account ending 4750
  Your PO: PO-2026-2009
  BAK-VSP-12     Victoria sponge, 12 slices                       qty   5 @    £16.15  VAT  0%  net     £80.75
  BAK-SHB-12     All-butter shortbread fingers 150g (case of 12)  qty   6 @    £15.15  VAT  0%  net     £90.90
  BAK-SCN-24     Fruit scones (tray of 24)                        qty  10 @    £13.32  VAT  0%  net    £133.20
  BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty   4 @    £12.06  VAT  0%  net     £48.24
  Net: £353.09   VAT: £0.00
  Total due: £353.09

PREVIOUS INVOICES FROM THIS SUPPLIER
  (none)

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 20. case-01192: UNAPPLIED_CREDIT (partly_applied, hard)

Money at risk if wrongly approved: £11.38

Rule that decides it: UNAPPLIED_CREDIT: must be deducted in full.

```
SUPPLIER RECORD
  Name: Redmire Biscuit Company Ltd
  Also trades as: Redmire Biscuit Company, Redmire Biscuit
  VAT number: GB 539 3363 38
  Bank account on file: ending 8073
  Contract pricing: variable

PURCHASE ORDER PO-2026-2067 (raised 28 Sep 2026)
  BAK-VSP-12     Victoria sponge, 12 slices                       qty   5 @    £15.51
  BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty   3 @    £11.64
  BAK-SCN-24     Fruit scones (tray of 24)                        qty  11 @    £15.23
  SNK-SPW-24     Sparkling spring water 500ml (case of 24)        qty   2 @     £9.86

GOODS RECEIVED
  GRN-16501 (29 Sep 2026): BAK-VSP-12 x5, BAK-DIG-12 x3, BAK-SCN-24 x11, SNK-SPW-24 x2

INVOICE RED-38012 (dated 2 Oct 2026)
  From: Redmire Biscuit Company Ltd
  VAT number: GB 539 3363 38
  Pay to: account ending 8073
  Your PO: PO-2026-2067
  BAK-VSP-12     Victoria sponge, 12 slices                       qty   5 @    £15.51  VAT  0%  net     £77.55
  BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty   3 @    £11.64  VAT  0%  net     £34.92
  BAK-SCN-24     Fruit scones (tray of 24)                        qty  11 @    £15.23  VAT  0%  net    £167.53
  SNK-SPW-24     Sparkling spring water 500ml (case of 24)        qty   2 @     £9.86  VAT 20%  net     £19.72
  Net: £299.72   VAT: £3.94
  Less credit CN-9140: £11.37
  Total due: £292.29
  Note: Less credit note CN-9140.

PREVIOUS INVOICES FROM THIS SUPPLIER
  RED-37717 (26 Jun 2026), PO PO-2026-1681, total £58.32, paid
    SNK-SPW-24     Sparkling spring water 500ml (case of 24)        qty   5 @     £9.72  VAT 20%  net     £48.60
  RED-37957 (14 Sep 2026), PO PO-2026-1976, total £391.49, paid
    BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty  11 @    £12.25  VAT  0%  net    £134.75
    SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty   5 @    £15.59  VAT 20%  net     £77.95
    SNK-CDG-12     Milk chocolate digestives 300g (case of 12)      qty  10 @    £13.60  VAT 20%  net    £136.00
  RED-37974 (20 Sep 2026), PO PO-2026-2023, total £303.36, paid
    SNK-CRS-24     Sea salt crisps 40g (case of 24)                 qty   8 @    £11.05  VAT 20%  net     £88.40
    BAK-VSP-12     Victoria sponge, 12 slices                       qty  12 @    £16.44  VAT  0%  net    £197.28

OPEN CREDIT NOTES FROM THIS SUPPLIER
  CN-9140 (16 Sep 2026), £22.75, PO PO-2026-2067: Damaged items on delivery. To be deducted from your next invoice against PO-2026-2067.
```

Your notes:

## 21. case-00286: TAX_ERROR (plain_biscuit_at_standard, hard)

Money at risk if wrongly approved: £21.98

Rule that decides it: TAX_ERROR: plain biscuits (including shortbread) are 0%.

**Possible disagreement:** Relies on the reader treating shortbread as a biscuit. Check you agree.

```
SUPPLIER RECORD
  Name: Fenwick Wholesale Ltd
  Also trades as: Fenwick Wholesale
  VAT number: GB 684 9340 72
  Bank account on file: ending 2581
  Contract pricing: fixed

PURCHASE ORDER PO-2026-1755 (raised 12 Jul 2026)
  COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   7 @    £25.96
  SNK-SPW-24     Sparkling spring water 500ml (case of 24)        qty   5 @     £9.24
  DRY-CRM-1L     Double cream 1L                                  qty  43 @     £3.93
  BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty   9 @    £12.21
  Note: Deliver to Market Street branch.

GOODS RECEIVED
  GRN-17097 (13 Jul 2026): COF-DEC-1K x7, SNK-SPW-24 x5, DRY-CRM-1L x43, BAK-DIG-12 x9
    Note: Chilled items checked on arrival.

INVOICE FEN-78569 (dated 13 Jul 2026)
  From: Fenwick Wholesale Ltd
  VAT number: GB 684 9340 72
  Pay to: account ending 2581
  Your PO: PO-2026-1755
  COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   7 @    £25.96  VAT  0%  net    £181.72
  SNK-SPW-24     Sparkling spring water 500ml (case of 24)        qty   5 @     £9.24  VAT 20%  net     £46.20
  DRY-CRM-1L     Double cream 1L                                  qty  43 @     £3.93  VAT  0%  net    £168.99
  BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty   9 @    £12.21  VAT 20%  net    £109.89
  Net: £506.80   VAT: £31.22
  Total due: £538.02

PREVIOUS INVOICES FROM THIS SUPPLIER
  FEN-78384 (13 May 2026), PO PO-2026-1486, total £269.04, paid
    DRY-CRM-1L     Double cream 1L                                  qty  26 @     £3.87  VAT  0%  net    £100.62
    BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty  14 @    £12.03  VAT  0%  net    £168.42

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 22. case-00745: DUPLICATE (reformatted_number, hard)

Money at risk if wrongly approved: £428.28

Rule that decides it: DUPLICATE: same goods on the same PO, whatever the invoice number or date.

**Possible disagreement:** Arrives as a payment reminder. Still a duplicate, because the original was already paid.

```
SUPPLIER RECORD
  Name: Netherby Catering Engineers Ltd
  Also trades as: Netherby Catering Engineers, Netherby Catering
  VAT number: GB 371 6786 84
  Bank account on file: ending 3525
  Contract pricing: variable

PURCHASE ORDER PO-2026-2097 (raised 6 Oct 2026)
  EQP-FLT-CART   Water filter cartridge                           qty   1 @    £70.76
  EQP-SVC-VISIT  Espresso machine service visit                   qty   2 @   £143.07

GOODS RECEIVED
  GRN-73843 (12 Oct 2026): EQP-FLT-CART x1, EQP-SVC-VISIT x2
    Note: Engineer visit completed.

INVOICE NET-75456 (dated 1 Nov 2026)
  From: Netherby Catering Engineers Ltd
  VAT number: GB 371 6786 84
  Pay to: account ending 3525
  Your PO: PO-2026-2097
  EQP-FLT-CART   Water filter cartridge                           qty   1 @    £70.76  VAT 20%  net     £70.76
  EQP-SVC-VISIT  Espresso machine service visit                   qty   2 @   £143.07  VAT 20%  net    £286.14
  Net: £356.90   VAT: £71.38
  Total due: £428.28
  Note: Please quote the invoice number on your remittance.
  Note: Second request for payment.

PREVIOUS INVOICES FROM THIS SUPPLIER
  NET-75219 (30 Jul 2026), PO PO-2026-1800, total £185.62, paid
    EQP-SVC-VISIT  Espresso machine service visit                   qty   1 @   £154.68  VAT 20%  net    £154.68
  NET-75231 (3 Aug 2026), PO PO-2026-1830, total £453.95, paid
    EQP-SVC-VISIT  Espresso machine service visit                   qty   2 @   £153.67  VAT 20%  net    £307.34
    EQP-FLT-CART   Water filter cartridge                           qty   1 @    £70.95  VAT 20%  net     £70.95
  NET-75240 (6 Aug 2026), PO PO-2026-1839, total £414.34, paid
    EQP-SVC-VISIT  Espresso machine service visit                   qty   2 @   £139.32  VAT 20%  net    £278.64
    EQP-FLT-CART   Water filter cartridge                           qty   1 @    £66.64  VAT 20%  net     £66.64
  net-75456 (17 Oct 2026), PO PO-2026-2097, total £428.28, paid
    EQP-FLT-CART   Water filter cartridge                           qty   1 @    £70.76  VAT 20%  net     £70.76
    EQP-SVC-VISIT  Espresso machine service visit                   qty   2 @   £143.07  VAT 20%  net    £286.14

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 23. case-00354: QUANTITY_VARIANCE (overbilled, easy)

Money at risk if wrongly approved: £82.54

Rule that decides it: QUANTITY_VARIANCE: invoiced exceeds delivered.

```
SUPPLIER RECORD
  Name: Glenholt Espresso Services Ltd
  Also trades as: Glenholt Espresso Services, Glenholt Espresso
  VAT number: GB 726 1675 13
  Bank account on file: ending 7017
  Contract pricing: fixed

PURCHASE ORDER PO-2026-1965 (raised 3 Sep 2026)
  EQP-FLT-CART   Water filter cartridge                           qty   1 @    £68.78
  EQP-SVC-VISIT  Espresso machine service visit                   qty   2 @   £142.58

GOODS RECEIVED
  GRN-17780 (6 Sep 2026): EQP-FLT-CART x1, EQP-SVC-VISIT x2

INVOICE GLE-58335 (dated 7 Sep 2026)
  From: Glenholt Espresso Services Ltd
  VAT number: GB 726 1675 13
  Pay to: account ending 7017
  Your PO: PO-2026-1965
  EQP-FLT-CART   Water filter cartridge                           qty   2 @    £68.78  VAT 20%  net    £137.56
  EQP-SVC-VISIT  Espresso machine service visit                   qty   2 @   £142.58  VAT 20%  net    £285.16
  Net: £422.72   VAT: £84.54
  Total due: £507.26

PREVIOUS INVOICES FROM THIS SUPPLIER
  GLE-58153 (8 Jul 2026), PO PO-2026-1718, total £87.10, paid
    EQP-FLT-CART   Water filter cartridge                           qty   1 @    £72.58  VAT 20%  net     £72.58
  GLE-58168 (13 Jul 2026), PO PO-2026-1744, total £359.62, paid
    EQP-SVC-VISIT  Espresso machine service visit                   qty   2 @   £149.84  VAT 20%  net    £299.68
  GLE-58296 (25 Aug 2026), PO PO-2026-1919, total £185.10, paid
    EQP-SVC-VISIT  Espresso machine service visit                   qty   1 @   £154.25  VAT 20%  net    £154.25

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 24. case-00260: PRICE_VARIANCE (just_over, hard)

Money at risk if wrongly approved: £12.72

Rule that decides it: PRICE_VARIANCE: above the 2% tolerance.

```
SUPPLIER RECORD
  Name: Farleigh Dairies Ltd
  Also trades as: Farleigh Dairies
  VAT number: GB 304 3483 95
  Bank account on file: ending 4249
  Contract pricing: variable

PURCHASE ORDER PO-2026-1861 (raised 8 Aug 2026)
  DRY-WHL-6      Whole milk 2L (case of 6)                        qty  38 @     £7.88
  DRY-SSK-6      Semi-skimmed milk 2L (case of 6)                 qty  53 @     £7.00
  DRY-CRM-1L     Double cream 1L                                  qty  49 @     £4.31

GOODS RECEIVED
  GRN-62469 (9 Aug 2026): DRY-WHL-6 x38, DRY-SSK-6 x53, DRY-CRM-1L x49

INVOICE FAR-48048 (dated 9 Aug 2026)
  From: Farleigh Dairies Ltd
  VAT number: GB 304 3483 95
  Pay to: account ending 4249
  Your PO: PO-2026-1861
  DRY-WHL-6      Whole milk 2L (case of 6)                        qty  38 @     £7.88  VAT  0%  net    £299.44
  DRY-SSK-6      Semi-skimmed milk 2L (case of 6)                 qty  53 @     £7.24  VAT  0%  net    £383.72
  DRY-CRM-1L     Double cream 1L                                  qty  49 @     £4.31  VAT  0%  net    £211.19
  Net: £894.35   VAT: £0.00
  Total due: £894.35

PREVIOUS INVOICES FROM THIS SUPPLIER
  (none)

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 25. case-00783: SUPPLIER_MISMATCH (different_vat, easy)

Money at risk if wrongly approved: £398.09

Rule that decides it: SUPPLIER_MISMATCH: VAT number does not match the supplier record.

```
SUPPLIER RECORD
  Name: Marston Leaf & Bean Ltd
  Also trades as: Marston Leaf & Bean, Marston Leaf
  VAT number: GB 505 8770 65
  Bank account on file: ending 8477
  Contract pricing: variable

PURCHASE ORDER PO-2026-1878 (raised 12 Aug 2026)
  TEA-EGL-500    Earl Grey loose leaf tea 500g                    qty   7 @    £15.85
  COF-COL-1K     Colombian coffee beans 1kg                       qty   8 @    £21.53
  TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   5 @    £22.98
  Note: Deliver before 8am.

GOODS RECEIVED
  GRN-77612 (16 Aug 2026): TEA-EGL-500 x7, COF-COL-1K x8, TEA-ASM-1K x5
    Note: Left with front-of-house staff.

INVOICE MAR-63379 (dated 19 Aug 2026)
  From: Marston Leaf & Bean Ltd
  VAT number: GB 972 2820 81
  Pay to: account ending 8477
  Your PO: PO-2026-1878
  TEA-EGL-500    Earl Grey loose leaf tea 500g                    qty   7 @    £15.85  VAT  0%  net    £110.95
  COF-COL-1K     Colombian coffee beans 1kg                       qty   8 @    £21.53  VAT  0%  net    £172.24
  TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   5 @    £22.98  VAT  0%  net    £114.90
  Net: £398.09   VAT: £0.00
  Total due: £398.09

PREVIOUS INVOICES FROM THIS SUPPLIER
  (none)

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 26. case-00194: PRICE_VARIANCE (uplift_not_yet_effective, hard)

Money at risk if wrongly approved: £32.10

Rule that decides it: PRICE_VARIANCE: the invoice is dated before the agreed change takes effect.

```
SUPPLIER RECORD
  Name: Ingleby Foodservice Ltd
  Also trades as: Ingleby Foodservice
  VAT number: GB 261 4014 19
  Bank account on file: ending 3643
  Contract pricing: fixed

PURCHASE ORDER PO-2026-2018 (raised 16 Sep 2026)
  BAK-VSP-12     Victoria sponge, 12 slices                       qty  14 @    £17.17
  COF-COL-1K     Colombian coffee beans 1kg                       qty   8 @    £23.35
  SNK-CDG-12     Milk chocolate digestives 300g (case of 12)      qty   2 @    £13.30
  SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty   4 @    £15.82
  Note: Supplier price review: 6% uplift agreed by Purchasing, applies from 27 October 2026.

GOODS RECEIVED
  GRN-97188 (17 Sep 2026): BAK-VSP-12 x14, COF-COL-1K x8, SNK-CDG-12 x2, SNK-CSB-12 x4

INVOICE ING-68565 (dated 17 Sep 2026)
  From: Ingleby Foodservice Ltd
  VAT number: GB 261 4014 19
  Pay to: account ending 3643
  Your PO: PO-2026-2018
  BAK-VSP-12     Victoria sponge, 12 slices                       qty  14 @    £18.20  VAT  0%  net    £254.80
  COF-COL-1K     Colombian coffee beans 1kg                       qty   8 @    £24.75  VAT  0%  net    £198.00
  SNK-CDG-12     Milk chocolate digestives 300g (case of 12)      qty   2 @    £14.10  VAT 20%  net     £28.20
  SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty   4 @    £16.77  VAT 20%  net     £67.08
  Net: £548.08   VAT: £19.06
  Total due: £567.14

PREVIOUS INVOICES FROM THIS SUPPLIER
  ING-68226 (27 May 2026), PO PO-2026-1563, total £245.01, paid
    SNK-SPW-24     Sparkling spring water 500ml (case of 24)        qty   9 @    £10.33  VAT 20%  net     £92.97
    DRY-WHL-6      Whole milk 2L (case of 6)                        qty  17 @     £7.85  VAT  0%  net    £133.45
  ING-68300 (20 Jun 2026), PO PO-2026-1648, total £396.42, paid
    TEA-EBT-1100   English breakfast tea bags (box of 1,100)        qty  11 @    £18.17  VAT  0%  net    £199.87
    SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty  11 @    £14.89  VAT 20%  net    £163.79
  ING-68469 (16 Aug 2026), PO PO-2026-1877, total £557.88, paid
    COF-COL-1K     Colombian coffee beans 1kg                       qty   8 @    £22.29  VAT  0%  net    £178.32
    DRY-CRM-1L     Double cream 1L                                  qty  54 @     £4.10  VAT  0%  net    £221.40
    SNK-CDG-12     Milk chocolate digestives 300g (case of 12)      qty  10 @    £13.18  VAT 20%  net    £131.80

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 27. case-00245: DUPLICATE (same_number, easy)

Money at risk if wrongly approved: £358.35

Rule that decides it: DUPLICATE: same goods already billed on the same PO.

```
SUPPLIER RECORD
  Name: Redmire Biscuit Company Ltd
  Also trades as: Redmire Biscuit Company, Redmire Biscuit
  VAT number: GB 539 3363 38
  Bank account on file: ending 8073
  Contract pricing: variable

PURCHASE ORDER PO-2026-1886 (raised 14 Aug 2026)
  SNK-CRS-24     Sea salt crisps 40g (case of 24)                 qty   8 @    £11.22
  BAK-SCN-24     Fruit scones (tray of 24)                        qty   4 @    £15.08
  SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty  10 @    £15.86

GOODS RECEIVED
  GRN-49231 (19 Aug 2026): SNK-CRS-24 x8, BAK-SCN-24 x4, SNK-CSB-12 x10

INVOICE RED-37885 (dated 21 Aug 2026)
  From: Redmire Biscuit Company Ltd
  VAT number: GB 539 3363 38
  Pay to: account ending 8073
  Your PO: PO-2026-1886
  SNK-CRS-24     Sea salt crisps 40g (case of 24)                 qty   8 @    £11.22  VAT 20%  net     £89.76
  BAK-SCN-24     Fruit scones (tray of 24)                        qty   4 @    £15.08  VAT  0%  net     £60.32
  SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty  10 @    £15.86  VAT 20%  net    £158.60
  Net: £308.68   VAT: £49.67
  Total due: £358.35

PREVIOUS INVOICES FROM THIS SUPPLIER
  RED-37694 (18 Jun 2026), PO PO-2026-1644, total £300.05, paid
    BAK-VSP-12     Victoria sponge, 12 slices                       qty   6 @    £16.19  VAT  0%  net     £97.14
    BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty   6 @    £12.23  VAT  0%  net     £73.38
    SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty   7 @    £15.42  VAT 20%  net    £107.94
  RED-37735 (2 Jul 2026), PO PO-2026-1687, total £166.44, paid
    SNK-CDG-12     Milk chocolate digestives 300g (case of 12)      qty  10 @    £13.87  VAT 20%  net    £138.70
  RED-37885 (11 Aug 2026), PO PO-2026-1886, total £358.35, paid
    SNK-CRS-24     Sea salt crisps 40g (case of 24)                 qty   8 @    £11.22  VAT 20%  net     £89.76
    BAK-SCN-24     Fruit scones (tray of 24)                        qty   4 @    £15.08  VAT  0%  net     £60.32
    SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty  10 @    £15.86  VAT 20%  net    £158.60

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 28. case-00826: TAX_ERROR (zero_on_standard_rated, hard)

Money at risk if wrongly approved: £9.21

Rule that decides it: TAX_ERROR: chocolate biscuits, crisps and bottled water are 20%.

```
SUPPLIER RECORD
  Name: Eskdale Wholesale Ltd
  Also trades as: Eskdale Wholesale
  VAT number: GB 047 4395 75
  Bank account on file: ending 5974
  Contract pricing: fixed

PURCHASE ORDER PO-2026-1621 (raised 9 Jun 2026)
  TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   8 @    £23.53
  COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   5 @    £25.31
  DRY-SSK-6      Semi-skimmed milk 2L (case of 6)                 qty  16 @     £7.39
  SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty   3 @    £15.35

GOODS RECEIVED
  GRN-80782 (14 Jun 2026): TEA-ASM-1K x8, COF-DEC-1K x5, DRY-SSK-6 x16, SNK-CSB-12 x3
    Note: Delivered to rear entrance.

INVOICE ESK-39397 (dated 19 Jun 2026)
  From: Eskdale Wholesale Ltd
  VAT number: GB 047 4395 75
  Pay to: account ending 5974
  Your PO: PO-2026-1621
  TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   8 @    £23.53  VAT  0%  net    £188.24
  COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   5 @    £25.31  VAT  0%  net    £126.55
  DRY-SSK-6      Semi-skimmed milk 2L (case of 6)                 qty  16 @     £7.39  VAT  0%  net    £118.24
  SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty   3 @    £15.35  VAT  0%  net     £46.05
  Net: £479.08   VAT: £0.00
  Total due: £479.08

PREVIOUS INVOICES FROM THIS SUPPLIER
  ESK-39017 (13 Feb 2026), PO PO-2026-1133, total £328.94, paid
    TEA-EGL-500    Earl Grey loose leaf tea 500g                    qty   6 @    £15.47  VAT  0%  net     £92.82
    COF-COL-1K     Colombian coffee beans 1kg                       qty   2 @    £23.02  VAT  0%  net     £46.04
    DRY-WHL-6      Whole milk 2L (case of 6)                        qty  24 @     £7.92  VAT  0%  net    £190.08

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 29. case-01441: QUANTITY_VARIANCE (billed_full_on_partial, hard)

Money at risk if wrongly approved: £35.98

Rule that decides it: QUANTITY_VARIANCE: invoiced exceeds delivered.

```
SUPPLIER RECORD
  Name: Radley Tea Company Ltd
  Also trades as: Radley Tea Company, Radley Tea
  VAT number: GB 603 1372 15
  Bank account on file: ending 9842
  Contract pricing: fixed

PURCHASE ORDER PO-2026-1801 (raised 24 Jul 2026)
  TEA-EBT-1100   English breakfast tea bags (box of 1,100)        qty   5 @    £17.99
  TEA-EGL-500    Earl Grey loose leaf tea 500g                    qty  11 @    £17.74
  TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   5 @    £23.25

GOODS RECEIVED
  GRN-61464 (28 Jul 2026): TEA-EBT-1100 x3, TEA-EGL-500 x11, TEA-ASM-1K x5
    Note: Partial shipment. Outstanding quantity to follow.

INVOICE RAD-29324 (dated 1 Aug 2026)
  From: Radley Tea Company Ltd
  VAT number: GB 603 1372 15
  Pay to: account ending 9842
  Your PO: PO-2026-1801
  TEA-EBT-1100   English breakfast tea bags (box of 1,100)        qty   5 @    £17.99  VAT  0%  net     £89.95
  TEA-EGL-500    Earl Grey loose leaf tea 500g                    qty  11 @    £17.74  VAT  0%  net    £195.14
  TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   5 @    £23.25  VAT  0%  net    £116.25
  Net: £401.34   VAT: £0.00
  Total due: £401.34

PREVIOUS INVOICES FROM THIS SUPPLIER
  RAD-28960 (1 Apr 2026), PO PO-2026-1317, total £290.41, paid
    COF-COL-1K     Colombian coffee beans 1kg                       qty   4 @    £24.34  VAT  0%  net     £97.36
    TEA-EBT-1100   English breakfast tea bags (box of 1,100)        qty  11 @    £17.55  VAT  0%  net    £193.05
  RAD-29022 (22 Apr 2026), PO PO-2026-1400, total £288.97, paid
    COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty  11 @    £26.27  VAT  0%  net    £288.97
  RAD-29274 (15 Jul 2026), PO PO-2026-1758, total £273.13, paid
    TEA-ASM-1K     Assam loose leaf tea 1kg                         qty  11 @    £24.83  VAT  0%  net    £273.13

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 30. case-00608: APPROVE (clean, easy)

Money at risk if wrongly approved: £0.00

Rule that decides it: Nothing in the policy applies.

```
SUPPLIER RECORD
  Name: Oakhurst Tea Company Ltd
  Also trades as: Oakhurst Tea Company, Oakhurst Tea
  VAT number: GB 326 5020 14
  Bank account on file: ending 7057
  Contract pricing: fixed

PURCHASE ORDER PO-2026-1520 (raised 15 May 2026)
  TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   2 @    £23.30
  COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty  12 @    £26.15
  COF-COL-1K     Colombian coffee beans 1kg                       qty   5 @    £22.36
  TEA-EBT-1100   English breakfast tea bags (box of 1,100)        qty   8 @    £17.55
  Note: Deliver to Market Street branch.

GOODS RECEIVED
  GRN-84003 (17 May 2026): TEA-ASM-1K x2, COF-DEC-1K x12, COF-COL-1K x5, TEA-EBT-1100 x8

INVOICE OAK-76708 (dated 21 May 2026)
  From: Oakhurst Tea Company Ltd
  VAT number: GB 326 5020 14
  Pay to: account ending 7057
  Your PO: PO-2026-1520
  TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   2 @    £23.30  VAT  0%  net     £46.60
  COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty  12 @    £26.15  VAT  0%  net    £313.80
  COF-COL-1K     Colombian coffee beans 1kg                       qty   5 @    £22.36  VAT  0%  net    £111.80
  TEA-EBT-1100   English breakfast tea bags (box of 1,100)        qty   8 @    £17.55  VAT  0%  net    £140.40
  Net: £612.60   VAT: £0.00
  Total due: £612.60
  Note: Thank you for your custom.

PREVIOUS INVOICES FROM THIS SUPPLIER
  OAK-76578 (7 Apr 2026), PO PO-2026-1354, total £106.20, paid
    COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   4 @    £26.55  VAT  0%  net    £106.20

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 31. case-00287: DUPLICATE (new_number, hard)

Money at risk if wrongly approved: £264.52

Rule that decides it: DUPLICATE: same goods on the same PO, whatever the invoice number.

```
SUPPLIER RECORD
  Name: Brockley Fine Foods Ltd
  Also trades as: Brockley Fine Foods, Brockley Fine
  VAT number: GB 595 7117 77
  Bank account on file: ending 7927
  Contract pricing: fixed

PURCHASE ORDER PO-2026-1531 (raised 17 May 2026)
  BAK-VSP-12     Victoria sponge, 12 slices                       qty   6 @    £15.49
  SNK-SPW-24     Sparkling spring water 500ml (case of 24)        qty   6 @     £9.75
  SNK-CDG-12     Milk chocolate digestives 300g (case of 12)      qty   6 @    £14.08

GOODS RECEIVED
  GRN-24994 (19 May 2026): BAK-VSP-12 x6, SNK-SPW-24 x6, SNK-CDG-12 x6

INVOICE BRO-32515 (dated 23 May 2026)
  From: Brockley Fine Foods Ltd
  VAT number: GB 595 7117 77
  Pay to: account ending 7927
  Your PO: PO-2026-1531
  BAK-VSP-12     Victoria sponge, 12 slices                       qty   6 @    £15.49  VAT  0%  net     £92.94
  SNK-SPW-24     Sparkling spring water 500ml (case of 24)        qty   6 @     £9.75  VAT 20%  net     £58.50
  SNK-CDG-12     Milk chocolate digestives 300g (case of 12)      qty   6 @    £14.08  VAT 20%  net     £84.48
  Net: £235.92   VAT: £28.60
  Total due: £264.52

PREVIOUS INVOICES FROM THIS SUPPLIER
  BRO-32259 (27 Feb 2026), PO PO-2026-1183, total £336.08, paid
    SNK-CDG-12     Milk chocolate digestives 300g (case of 12)      qty  11 @    £13.04  VAT 20%  net    £143.44
    BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty  15 @    £10.93  VAT  0%  net    £163.95
  BRO-32470 (8 May 2026), PO PO-2026-1531, total £264.52, paid
    BAK-VSP-12     Victoria sponge, 12 slices                       qty   6 @    £15.49  VAT  0%  net     £92.94
    SNK-SPW-24     Sparkling spring water 500ml (case of 24)        qty   6 @     £9.75  VAT 20%  net     £58.50
    SNK-CDG-12     Milk chocolate digestives 300g (case of 12)      qty   6 @    £14.08  VAT 20%  net     £84.48

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 32. case-01967: APPROVE (partial_second_invoice, hard)

Money at risk if wrongly approved: £0.00

Rule that decides it: QUANTITY_VARIANCE: counts all invoices on the PO against all deliveries.

```
SUPPLIER RECORD
  Name: Stanwick Bakery Supplies Ltd
  Also trades as: Stanwick Bakery Supplies, Stanwick Bakery
  VAT number: GB 878 0175 98
  Bank account on file: ending 9930
  Contract pricing: variable

PURCHASE ORDER PO-2026-2047 (raised 23 Sep 2026)
  BAK-SCN-24     Fruit scones (tray of 24)                        qty  12 @    £13.81
  BAK-VSP-12     Victoria sponge, 12 slices                       qty   4 @    £17.01
  SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty   6 @    £16.74

GOODS RECEIVED
  GRN-18837 (25 Sep 2026): BAK-SCN-24 x8, BAK-VSP-12 x3, SNK-CSB-12 x4
    Note: Short delivery: remaining items on back order.
  GRN-25748 (2 Oct 2026): BAK-SCN-24 x4, BAK-VSP-12 x1, SNK-CSB-12 x2

INVOICE STA-55016 (dated 4 Oct 2026)
  From: Stanwick Bakery Supplies Ltd
  VAT number: GB 878 0175 98
  Pay to: account ending 9930
  Your PO: PO-2026-2047
  BAK-SCN-24     Fruit scones (tray of 24)                        qty   4 @    £13.81  VAT  0%  net     £55.24
  BAK-VSP-12     Victoria sponge, 12 slices                       qty   1 @    £17.01  VAT  0%  net     £17.01
  SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty   2 @    £16.74  VAT 20%  net     £33.48
  Net: £105.73   VAT: £6.70
  Total due: £112.43
  Note: Thank you for your custom.

PREVIOUS INVOICES FROM THIS SUPPLIER
  STA-54729 (30 Jun 2026), PO PO-2026-1691, total £241.57, paid
    BAK-SCN-24     Fruit scones (tray of 24)                        qty  11 @    £13.61  VAT  0%  net    £149.71
    BAK-VSP-12     Victoria sponge, 12 slices                       qty   6 @    £15.31  VAT  0%  net     £91.86
  STA-54991 (25 Sep 2026), PO PO-2026-2047, total £241.86, paid
    BAK-SCN-24     Fruit scones (tray of 24)                        qty   8 @    £13.81  VAT  0%  net    £110.48
    BAK-VSP-12     Victoria sponge, 12 slices                       qty   3 @    £17.01  VAT  0%  net     £51.03
    SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty   4 @    £16.74  VAT 20%  net     £66.96

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 33. case-00054: APPROVE (standing_order, hard)

Money at risk if wrongly approved: £0.00

Rule that decides it: DUPLICATE: standing orders on different POs are not duplicates.

```
SUPPLIER RECORD
  Name: Calder Wholesale Ltd
  Also trades as: Calder Wholesale
  VAT number: GB 154 7280 38
  Bank account on file: ending 5926
  Contract pricing: fixed

PURCHASE ORDER PO-2026-1696 (raised 28 Jun 2026)
  TEA-ASM-1K     Assam loose leaf tea 1kg                         qty  10 @    £23.59
  COF-COL-1K     Colombian coffee beans 1kg                       qty   7 @    £21.30
  SNK-CDG-12     Milk chocolate digestives 300g (case of 12)      qty  12 @    £12.72
  Note: Standing weekly order.

GOODS RECEIVED
  GRN-21733 (3 Jul 2026): TEA-ASM-1K x10, COF-COL-1K x7, SNK-CDG-12 x12

INVOICE CAL-34338 (dated 3 Jul 2026)
  From: Calder Wholesale Ltd
  VAT number: GB 154 7280 38
  Pay to: account ending 5926
  Your PO: PO-2026-1696
  TEA-ASM-1K     Assam loose leaf tea 1kg                         qty  10 @    £23.59  VAT  0%  net    £235.90
  COF-COL-1K     Colombian coffee beans 1kg                       qty   7 @    £21.30  VAT  0%  net    £149.10
  SNK-CDG-12     Milk chocolate digestives 300g (case of 12)      qty  12 @    £12.72  VAT 20%  net    £152.64
  Net: £537.64   VAT: £30.53
  Total due: £568.17

PREVIOUS INVOICES FROM THIS SUPPLIER
  CAL-34295 (19 Jun 2026), PO PO-2026-1670, total £568.17, paid
    TEA-ASM-1K     Assam loose leaf tea 1kg                         qty  10 @    £23.59  VAT  0%  net    £235.90
    COF-COL-1K     Colombian coffee beans 1kg                       qty   7 @    £21.30  VAT  0%  net    £149.10
    SNK-CDG-12     Milk chocolate digestives 300g (case of 12)      qty  12 @    £12.72  VAT 20%  net    £152.64

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 34. case-00249: UNAPPLIED_CREDIT (credit_ignored, easy)

Money at risk if wrongly approved: £36.88

Rule that decides it: UNAPPLIED_CREDIT: open credit on this PO not deducted.

```
SUPPLIER RECORD
  Name: Harrowby Foodservice Ltd
  Also trades as: Harrowby Foodservice
  VAT number: GB 528 9078 66
  Bank account on file: ending 6536
  Contract pricing: variable

PURCHASE ORDER PO-2026-1968 (raised 4 Sep 2026)
  COF-COL-1K     Colombian coffee beans 1kg                       qty  12 @    £22.67
  DRY-CRM-1L     Double cream 1L                                  qty  37 @     £4.01
  Note: Contact the duty manager on arrival.

GOODS RECEIVED
  GRN-42142 (9 Sep 2026): COF-COL-1K x12, DRY-CRM-1L x37
    Note: Signed for by shift manager.

INVOICE HAR-27754 (dated 13 Sep 2026)
  From: Harrowby Foodservice Ltd
  VAT number: GB 528 9078 66
  Pay to: account ending 6536
  Your PO: PO-2026-1968
  COF-COL-1K     Colombian coffee beans 1kg                       qty  12 @    £22.67  VAT  0%  net    £272.04
  DRY-CRM-1L     Double cream 1L                                  qty  37 @     £4.01  VAT  0%  net    £148.37
  Net: £420.41   VAT: £0.00
  Total due: £420.41
  Note: Please quote the invoice number on your remittance.

PREVIOUS INVOICES FROM THIS SUPPLIER
  HAR-27400 (18 May 2026), PO PO-2026-1501, total £425.81, paid
    BAK-SCN-24     Fruit scones (tray of 24)                        qty  11 @    £14.22  VAT  0%  net    £156.42
    COF-COL-1K     Colombian coffee beans 1kg                       qty  11 @    £24.49  VAT  0%  net    £269.39
  HAR-27455 (5 Jun 2026), PO PO-2026-1590, total £501.92, paid
    DRY-WHL-6      Whole milk 2L (case of 6)                        qty  20 @     £7.42  VAT  0%  net    £148.40
    COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   3 @    £26.87  VAT  0%  net     £80.61
    TEA-ASM-1K     Assam loose leaf tea 1kg                         qty  11 @    £24.81  VAT  0%  net    £272.91
  HAR-27548 (6 Jul 2026), PO PO-2026-1716, total £708.33, paid
    SNK-CRS-24     Sea salt crisps 40g (case of 24)                 qty  12 @    £10.86  VAT 20%  net    £130.32
    DRY-SSK-6      Semi-skimmed milk 2L (case of 6)                 qty  52 @     £7.07  VAT  0%  net    £367.64
    COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   7 @    £26.33  VAT  0%  net    £184.31

OPEN CREDIT NOTES FROM THIS SUPPLIER
  CN-8282 (10 Sep 2026), £36.88, PO PO-2026-1968: Pricing error on previous invoice. To be deducted from your next invoice against PO-2026-1968.
```

Your notes:

## 35. case-00442: TAX_ERROR (vat_sum_wrong, easy)

Money at risk if wrongly approved: £1.15

Rule that decides it: TAX_ERROR: the VAT total must equal the sum of each line's VAT.

```
SUPPLIER RECORD
  Name: Kenley Farm Dairy Ltd
  Also trades as: Kenley Farm Dairy, Kenley Farm
  VAT number: GB 579 7543 23
  Bank account on file: ending 1341
  Contract pricing: variable

PURCHASE ORDER PO-2026-1534 (raised 18 May 2026)
  DRY-WHL-6      Whole milk 2L (case of 6)                        qty  58 @     £7.83
  DRY-SSK-6      Semi-skimmed milk 2L (case of 6)                 qty  37 @     £7.21
  DRY-CRM-1L     Double cream 1L                                  qty  33 @     £4.26

GOODS RECEIVED
  GRN-90060 (23 May 2026): DRY-WHL-6 x58, DRY-SSK-6 x37, DRY-CRM-1L x33

INVOICE KEN-13815 (dated 23 May 2026)
  From: Kenley Farm Dairy Ltd
  VAT number: GB 579 7543 23
  Pay to: account ending 1341
  Your PO: PO-2026-1534
  DRY-WHL-6      Whole milk 2L (case of 6)                        qty  58 @     £7.83  VAT  0%  net    £454.14
  DRY-SSK-6      Semi-skimmed milk 2L (case of 6)                 qty  37 @     £7.21  VAT  0%  net    £266.77
  DRY-CRM-1L     Double cream 1L                                  qty  33 @     £4.26  VAT  0%  net    £140.58
  Net: £861.49   VAT: £1.15
  Total due: £862.64

PREVIOUS INVOICES FROM THIS SUPPLIER
  KEN-13598 (12 Mar 2026), PO PO-2026-1252, total £374.76, paid
    DRY-WHL-6      Whole milk 2L (case of 6)                        qty  25 @     £8.43  VAT  0%  net    £210.75
    DRY-SSK-6      Semi-skimmed milk 2L (case of 6)                 qty  21 @     £7.81  VAT  0%  net    £164.01
  KEN-13613 (17 Mar 2026), PO PO-2026-1271, total £244.26, paid
    DRY-CRM-1L     Double cream 1L                                  qty  59 @     £4.14  VAT  0%  net    £244.26
  KEN-13628 (22 Mar 2026), PO PO-2026-1289, total £198.45, paid
    DRY-CRM-1L     Double cream 1L                                  qty  49 @     £4.05  VAT  0%  net    £198.45

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 36. case-00490: PRICE_VARIANCE (uplift_exceeded, hard)

Money at risk if wrongly approved: £9.49

Rule that decides it: PRICE_VARIANCE: tolerance applies to the agreed price, and the charge exceeds it.

```
SUPPLIER RECORD
  Name: Burnell Catering Engineers Ltd
  Also trades as: Burnell Catering Engineers, Burnell Catering
  VAT number: GB 846 5632 12
  Bank account on file: ending 2478
  Contract pricing: fixed

PURCHASE ORDER PO-2026-2072 (raised 30 Sep 2026)
  EQP-FLT-CART   Water filter cartridge                           qty   1 @    £73.43
  EQP-SVC-VISIT  Espresso machine service visit                   qty   1 @   £145.23
  Note: Deliver before 8am.
  Note: Price increase of 3% on all lines agreed with supplier, effective 3 October 2026.

GOODS RECEIVED
  GRN-70274 (2 Oct 2026): EQP-FLT-CART x1, EQP-SVC-VISIT x1

INVOICE BUR-24423 (dated 6 Oct 2026)
  From: Burnell Catering Engineers Ltd
  VAT number: GB 846 5632 12
  Pay to: account ending 2478
  Your PO: PO-2026-2072
  EQP-FLT-CART   Water filter cartridge                           qty   1 @    £78.29  VAT 20%  net     £78.29
  EQP-SVC-VISIT  Espresso machine service visit                   qty   1 @   £154.84  VAT 20%  net    £154.84
  Net: £233.13   VAT: £46.63
  Total due: £279.76

PREVIOUS INVOICES FROM THIS SUPPLIER
  BUR-24047 (3 Jun 2026), PO PO-2026-1584, total £343.61, paid
    EQP-SVC-VISIT  Espresso machine service visit                   qty   2 @   £143.17  VAT 20%  net    £286.34
  BUR-24050 (4 Jun 2026), PO PO-2026-1573, total £345.10, paid
    EQP-SVC-VISIT  Espresso machine service visit                   qty   2 @   £143.79  VAT 20%  net    £287.58
  BUR-24145 (5 Jul 2026), PO PO-2026-1702, total £165.86, paid
    EQP-SVC-VISIT  Espresso machine service visit                   qty   1 @   £138.22  VAT 20%  net    £138.22

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 37. case-01130: APPROVE (clean, easy)

Money at risk if wrongly approved: £0.00

Rule that decides it: Nothing in the policy applies.

```
SUPPLIER RECORD
  Name: Ingleby Foodservice Ltd
  Also trades as: Ingleby Foodservice
  VAT number: GB 261 4014 19
  Bank account on file: ending 3643
  Contract pricing: fixed

PURCHASE ORDER PO-2026-1983 (raised 7 Sep 2026)
  DRY-SSK-6      Semi-skimmed milk 2L (case of 6)                 qty  52 @     £7.27
  DRY-WHL-6      Whole milk 2L (case of 6)                        qty  13 @     £7.48
  BAK-SHB-12     All-butter shortbread fingers 150g (case of 12)  qty   9 @    £13.03
  SNK-SPW-24     Sparkling spring water 500ml (case of 24)        qty   7 @     £9.86

GOODS RECEIVED
  GRN-53126 (8 Sep 2026): DRY-SSK-6 x52, DRY-WHL-6 x13, BAK-SHB-12 x9, SNK-SPW-24 x7
    Note: Delivered to rear entrance.

INVOICE ING-68544 (dated 10 Sep 2026)
  From: Ingleby Foodservice Ltd
  VAT number: GB 261 4014 19
  Pay to: account ending 3643
  Your PO: PO-2026-1983
  DRY-SSK-6      Semi-skimmed milk 2L (case of 6)                 qty  52 @     £7.27  VAT  0%  net    £378.04
  DRY-WHL-6      Whole milk 2L (case of 6)                        qty  13 @     £7.48  VAT  0%  net     £97.24
  BAK-SHB-12     All-butter shortbread fingers 150g (case of 12)  qty   9 @    £13.03  VAT  0%  net    £117.27
  SNK-SPW-24     Sparkling spring water 500ml (case of 24)        qty   7 @     £9.86  VAT 20%  net     £69.02
  Net: £661.57   VAT: £13.80
  Total due: £675.37

PREVIOUS INVOICES FROM THIS SUPPLIER
  ING-68510 (29 Aug 2026), PO PO-2026-1921, total £464.26, paid
    BAK-SCN-24     Fruit scones (tray of 24)                        qty   7 @    £13.43  VAT  0%  net     £94.01
    DRY-WHL-6      Whole milk 2L (case of 6)                        qty  30 @     £8.04  VAT  0%  net    £241.20
    COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   5 @    £25.81  VAT  0%  net    £129.05

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 38. case-01652: APPROVE (credit_applied, hard)

Money at risk if wrongly approved: £0.00

Rule that decides it: UNAPPLIED_CREDIT: the credit is deducted in full.

```
SUPPLIER RECORD
  Name: Marston Leaf & Bean Ltd
  Also trades as: Marston Leaf & Bean, Marston Leaf
  VAT number: GB 505 8770 65
  Bank account on file: ending 8477
  Contract pricing: variable

PURCHASE ORDER PO-2026-1780 (raised 19 Jul 2026)
  TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   7 @    £24.48
  TEA-EGL-500    Earl Grey loose leaf tea 500g                    qty   7 @    £16.77
  COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   4 @    £27.00
  Note: Deliver before 8am.

GOODS RECEIVED
  GRN-41919 (25 Jul 2026): TEA-ASM-1K x7, TEA-EGL-500 x7, COF-DEC-1K x4

INVOICE MAR-63305 (dated 25 Jul 2026)
  From: Marston Leaf & Bean Ltd
  VAT number: GB 505 8770 65
  Pay to: account ending 8477
  Your PO: PO-2026-1780
  TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   7 @    £24.48  VAT  0%  net    £171.36
  TEA-EGL-500    Earl Grey loose leaf tea 500g                    qty   7 @    £16.77  VAT  0%  net    £117.39
  COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   4 @    £27.00  VAT  0%  net    £108.00
  Net: £396.75   VAT: £0.00
  Less credit CN-6926: £59.75
  Total due: £337.00
  Note: Less credit note CN-6926.

PREVIOUS INVOICES FROM THIS SUPPLIER
  MAR-63115 (23 May 2026), PO PO-2026-1521, total £696.79, paid
    TEA-EBT-1100   English breakfast tea bags (box of 1,100)        qty  11 @    £18.94  VAT  0%  net    £208.34
    COF-COL-1K     Colombian coffee beans 1kg                       qty   9 @    £23.68  VAT  0%  net    £213.12
    TEA-ASM-1K     Assam loose leaf tea 1kg                         qty  11 @    £25.03  VAT  0%  net    £275.33

OPEN CREDIT NOTES FROM THIS SUPPLIER
  CN-6926 (10 Jul 2026), £59.75, PO PO-2026-1780: Items missing from previous delivery. To be deducted from your next invoice against PO-2026-1780.
```

Your notes:

## 39. case-01562: PRICE_VARIANCE (fixed_contract_small, hard)

Money at risk if wrongly approved: £2.70

Rule that decides it: PRICE_VARIANCE: 0% tolerance on fixed-price contracts.

```
SUPPLIER RECORD
  Name: Ingleby Foodservice Ltd
  Also trades as: Ingleby Foodservice
  VAT number: GB 261 4014 19
  Bank account on file: ending 3643
  Contract pricing: fixed

PURCHASE ORDER PO-2026-1949 (raised 30 Aug 2026)
  BAK-SCN-24     Fruit scones (tray of 24)                        qty  10 @    £15.54
  BAK-SHB-12     All-butter shortbread fingers 150g (case of 12)  qty   2 @    £13.27
  SNK-CDG-12     Milk chocolate digestives 300g (case of 12)      qty  10 @    £13.37

GOODS RECEIVED
  GRN-17461 (3 Sep 2026): BAK-SCN-24 x10, BAK-SHB-12 x2, SNK-CDG-12 x10

INVOICE ING-68539 (dated 8 Sep 2026)
  From: Ingleby Foodservice Ltd
  VAT number: GB 261 4014 19
  Pay to: account ending 3643
  Your PO: PO-2026-1949
  BAK-SCN-24     Fruit scones (tray of 24)                        qty  10 @    £15.81  VAT  0%  net    £158.10
  BAK-SHB-12     All-butter shortbread fingers 150g (case of 12)  qty   2 @    £13.27  VAT  0%  net     £26.54
  SNK-CDG-12     Milk chocolate digestives 300g (case of 12)      qty  10 @    £13.37  VAT 20%  net    £133.70
  Net: £318.34   VAT: £26.74
  Total due: £345.08
  Note: Goods remain our property until paid in full.

PREVIOUS INVOICES FROM THIS SUPPLIER
  ING-68197 (17 May 2026), PO PO-2026-1510, total £544.52, paid
    SNK-SPW-24     Sparkling spring water 500ml (case of 24)        qty   5 @    £10.14  VAT 20%  net     £50.70
    TEA-EGL-500    Earl Grey loose leaf tea 500g                    qty   2 @    £17.44  VAT  0%  net     £34.88
    DRY-SSK-6      Semi-skimmed milk 2L (case of 6)                 qty  55 @     £8.16  VAT  0%  net    £448.80
  ING-68381 (17 Jul 2026), PO PO-2026-1767, total £78.60, paid
    TEA-EGL-500    Earl Grey loose leaf tea 500g                    qty   5 @    £15.72  VAT  0%  net     £78.60

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 40. case-00306: PRICE_VARIANCE (fixed_contract_small, hard)

Money at risk if wrongly approved: £1.80

Rule that decides it: PRICE_VARIANCE: 0% tolerance on fixed-price contracts.

```
SUPPLIER RECORD
  Name: Glenholt Espresso Services Ltd
  Also trades as: Glenholt Espresso Services, Glenholt Espresso
  VAT number: GB 726 1675 13
  Bank account on file: ending 7017
  Contract pricing: fixed

PURCHASE ORDER PO-2026-1949 (raised 30 Aug 2026)
  EQP-SVC-VISIT  Espresso machine service visit                   qty   1 @   £145.91
  EQP-FLT-CART   Water filter cartridge                           qty   2 @    £65.13

GOODS RECEIVED
  GRN-39892 (31 Aug 2026): EQP-SVC-VISIT x1, EQP-FLT-CART x2
    Note: Engineer visit completed.

INVOICE GLE-58325 (dated 3 Sep 2026)
  From: Glenholt Espresso Services Ltd
  VAT number: GB 726 1675 13
  Pay to: account ending 7017
  Your PO: PO-2026-1949
  EQP-SVC-VISIT  Espresso machine service visit                   qty   1 @   £147.41  VAT 20%  net    £147.41
  EQP-FLT-CART   Water filter cartridge                           qty   2 @    £65.13  VAT 20%  net    £130.26
  Net: £277.67   VAT: £55.53
  Total due: £333.20
  Note: Please quote the invoice number on your remittance.

PREVIOUS INVOICES FROM THIS SUPPLIER
  (none)

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:
