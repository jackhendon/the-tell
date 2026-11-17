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

```
</details>

## 1. case-00871: APPROVE (trading_name, hard)

Money at risk if wrongly approved: £0.00

Rule that decides it: SUPPLIER_MISMATCH: listed trading names are acceptable; the VAT number proves identity.

```
SUPPLIER RECORD
  Name: Elstow Catering Disposables Ltd
  Also trades as: Elstow Catering Disposables, Elstow Catering
  VAT number: GB 114 7104 97
  Bank account on file: ending 4662
  Contract pricing: variable

PURCHASE ORDER PO-2026-1688 (raised 26 Jun 2026)
  PKG-NAP-5000   Paper napkins (case of 5,000)                    qty   5 @    £27.35
  PKG-CUP-1000   12oz takeaway cups (case of 1,000)               qty   2 @    £61.20
  PKG-LID-1000   Sip lids for 12oz cups (case of 1,000)           qty   5 @    £29.93

GOODS RECEIVED
  GRN-68383 (1 Jul 2026): PKG-NAP-5000 x5, PKG-CUP-1000 x2, PKG-LID-1000 x5
    Note: Left with front-of-house staff.

INVOICE ELS-19039 (dated 3 Jul 2026)
  From: Elstow Catering
  VAT number: GB 114 7104 97
  Pay to: account ending 4662
  Your PO: PO-2026-1688
  PKG-NAP-5000   Paper napkins (case of 5,000)                    qty   5 @    £27.35  VAT 20%  net    £136.75
  PKG-CUP-1000   12oz takeaway cups (case of 1,000)               qty   2 @    £61.20  VAT 20%  net    £122.40
  PKG-LID-1000   Sip lids for 12oz cups (case of 1,000)           qty   5 @    £29.93  VAT 20%  net    £149.65
  Net: £408.80   VAT: £81.76
  Total due: £490.56
  Note: Please quote the invoice number on your remittance.

PREVIOUS INVOICES FROM THIS SUPPLIER
  (none)

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 2. case-01048: APPROVE (clean, easy)

Money at risk if wrongly approved: £0.00

Rule that decides it: Nothing in the policy applies.

```
SUPPLIER RECORD
  Name: Norland Biscuit Company Ltd
  Also trades as: Norland Biscuit Company, Norland Biscuit
  VAT number: GB 507 5291 70
  Bank account on file: ending 3575
  Contract pricing: variable

PURCHASE ORDER PO-2026-1574 (raised 28 May 2026)
  SNK-SPW-24     Sparkling spring water 500ml (case of 24)        qty   3 @     £9.72
  BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty   9 @    £11.18
  SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty   8 @    £14.37
  BAK-SCN-24     Fruit scones (tray of 24)                        qty   5 @    £13.99
  Note: Contact the duty manager on arrival.

GOODS RECEIVED
  GRN-20416 (29 May 2026): SNK-SPW-24 x3, BAK-DIG-12 x9, SNK-CSB-12 x8, BAK-SCN-24 x5

INVOICE NOR-20637 (dated 30 May 2026)
  From: Norland Biscuit Company Ltd
  VAT number: GB 507 5291 70
  Pay to: account ending 3575
  Your PO: PO-2026-1574
  SNK-SPW-24     Sparkling spring water 500ml (case of 24)        qty   3 @     £9.72  VAT 20%  net     £29.16
  BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty   9 @    £11.18  VAT  0%  net    £100.62
  SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty   8 @    £14.37  VAT 20%  net    £114.96
  BAK-SCN-24     Fruit scones (tray of 24)                        qty   5 @    £13.99  VAT  0%  net     £69.95
  Net: £314.69   VAT: £28.82
  Total due: £343.51

PREVIOUS INVOICES FROM THIS SUPPLIER
  NOR-20276 (30 Jan 2026), PO PO-2026-1087, total £211.03, paid
    SNK-CRS-24     Sea salt crisps 40g (case of 24)                 qty   8 @    £10.79  VAT 20%  net     £86.32
    BAK-SCN-24     Fruit scones (tray of 24)                        qty   7 @    £15.35  VAT  0%  net    £107.45

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 3. case-00186: APPROVE (mixed_vat, hard)

Money at risk if wrongly approved: £0.00

Rule that decides it: TAX_ERROR: VAT table, chocolate-covered biscuits 20%, plain biscuits 0%.

```
SUPPLIER RECORD
  Name: Brockley Fine Foods Ltd
  Also trades as: Brockley Fine Foods, Brockley Fine
  VAT number: GB 595 7117 77
  Bank account on file: ending 7927
  Contract pricing: fixed

PURCHASE ORDER PO-2026-1828 (raised 31 Jul 2026)
  BAK-SCN-24     Fruit scones (tray of 24)                        qty  15 @    £15.07
  BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty  10 @    £11.11
  BAK-VSP-12     Victoria sponge, 12 slices                       qty   7 @    £17.16
  SNK-CDG-12     Milk chocolate digestives 300g (case of 12)      qty   2 @    £12.35

GOODS RECEIVED
  GRN-26525 (5 Aug 2026): BAK-SCN-24 x15, BAK-DIG-12 x10, BAK-VSP-12 x7, SNK-CDG-12 x2

INVOICE BRO-32751 (dated 10 Aug 2026)
  From: Brockley Fine Foods Ltd
  VAT number: GB 595 7117 77
  Pay to: account ending 7927
  Your PO: PO-2026-1828
  BAK-SCN-24     Fruit scones (tray of 24)                        qty  15 @    £15.07  VAT  0%  net    £226.05
  BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty  10 @    £11.11  VAT  0%  net    £111.10
  BAK-VSP-12     Victoria sponge, 12 slices                       qty   7 @    £17.16  VAT  0%  net    £120.12
  SNK-CDG-12     Milk chocolate digestives 300g (case of 12)      qty   2 @    £12.35  VAT 20%  net     £24.70
  Net: £481.97   VAT: £4.94
  Total due: £486.91

PREVIOUS INVOICES FROM THIS SUPPLIER
  (none)

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 4. case-00825: UNAPPLIED_CREDIT (credit_ignored, easy)

Money at risk if wrongly approved: £38.02

Rule that decides it: UNAPPLIED_CREDIT: open credit on this PO not deducted.

```
SUPPLIER RECORD
  Name: Oakhurst Tea Company Ltd
  Also trades as: Oakhurst Tea Company, Oakhurst Tea
  VAT number: GB 326 5020 14
  Bank account on file: ending 7057
  Contract pricing: fixed

PURCHASE ORDER PO-2026-1568 (raised 27 May 2026)
  COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   2 @    £26.26
  TEA-EGL-500    Earl Grey loose leaf tea 500g                    qty  11 @    £15.84
  COF-COL-1K     Colombian coffee beans 1kg                       qty   8 @    £24.16

GOODS RECEIVED
  GRN-35316 (28 May 2026): COF-DEC-1K x2, TEA-EGL-500 x11, COF-COL-1K x8
    Note: Delivered to rear entrance.

INVOICE OAK-76741 (dated 1 Jun 2026)
  From: Oakhurst Tea Company Ltd
  VAT number: GB 326 5020 14
  Pay to: account ending 7057
  Your PO: PO-2026-1568
  COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   2 @    £26.26  VAT  0%  net     £52.52
  TEA-EGL-500    Earl Grey loose leaf tea 500g                    qty  11 @    £15.84  VAT  0%  net    £174.24
  COF-COL-1K     Colombian coffee beans 1kg                       qty   8 @    £24.16  VAT  0%  net    £193.28
  Net: £420.04   VAT: £0.00
  Total due: £420.04

PREVIOUS INVOICES FROM THIS SUPPLIER
  OAK-76448 (23 Feb 2026), PO PO-2026-1175, total £501.70, paid
    COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   5 @    £27.08  VAT  0%  net    £135.40
    COF-COL-1K     Colombian coffee beans 1kg                       qty   6 @    £23.28  VAT  0%  net    £139.68
    TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   9 @    £25.18  VAT  0%  net    £226.62
  OAK-76522 (20 Mar 2026), PO PO-2026-1274, total £356.04, paid
    COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   4 @    £25.77  VAT  0%  net    £103.08
    TEA-EBT-1100   English breakfast tea bags (box of 1,100)        qty   6 @    £19.80  VAT  0%  net    £118.80
    TEA-EGL-500    Earl Grey loose leaf tea 500g                    qty   8 @    £16.77  VAT  0%  net    £134.16
  OAK-76638 (27 Apr 2026), PO PO-2026-1433, total £391.01, paid
    TEA-ASM-1K     Assam loose leaf tea 1kg                         qty  11 @    £26.27  VAT  0%  net    £288.97
    COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   4 @    £25.51  VAT  0%  net    £102.04

OPEN CREDIT NOTES FROM THIS SUPPLIER
  CN-7958 (31 May 2026), £38.02, PO PO-2026-1568: Damaged items on delivery GRN-35316. To be deducted from your next invoice against PO-2026-1568.
```

Your notes:

## 5. case-00931: SUPPLIER_MISMATCH (lookalike_no_vat, hard)

Money at risk if wrongly approved: £452.21

Rule that decides it: SUPPLIER_MISMATCH: VAT number missing.

```
SUPPLIER RECORD
  Name: Hatherley Espresso Services Ltd
  Also trades as: Hatherley Espresso Services, Hatherley Espresso
  VAT number: GB 373 5379 90
  Bank account on file: ending 7855
  Contract pricing: variable

PURCHASE ORDER PO-2026-1939 (raised 27 Aug 2026)
  EQP-SVC-VISIT  Espresso machine service visit                   qty   2 @   £156.48
  EQP-FLT-CART   Water filter cartridge                           qty   1 @    £63.88

GOODS RECEIVED
  GRN-80775 (30 Aug 2026): EQP-SVC-VISIT x2, EQP-FLT-CART x1

INVOICE HAT-41323 (dated 3 Sep 2026)
  From: Hatherley Espresso Services Group Ltd
  VAT number: (not shown)
  Pay to: account ending 7855
  Your PO: PO-2026-1939
  EQP-SVC-VISIT  Espresso machine service visit                   qty   2 @   £156.48  VAT 20%  net    £312.96
  EQP-FLT-CART   Water filter cartridge                           qty   1 @    £63.88  VAT 20%  net     £63.88
  Net: £376.84   VAT: £75.37
  Total due: £452.21
  Note: Please quote the invoice number on your remittance.

PREVIOUS INVOICES FROM THIS SUPPLIER
  HAT-41090 (17 Jun 2026), PO PO-2026-1640, total £347.82, paid
    EQP-SVC-VISIT  Espresso machine service visit                   qty   1 @   £144.97  VAT 20%  net    £144.97
    EQP-FLT-CART   Water filter cartridge                           qty   2 @    £72.44  VAT 20%  net    £144.88
  HAT-41265 (14 Aug 2026), PO PO-2026-1878, total £259.48, paid
    EQP-FLT-CART   Water filter cartridge                           qty   1 @    £66.25  VAT 20%  net     £66.25
    EQP-SVC-VISIT  Espresso machine service visit                   qty   1 @   £149.98  VAT 20%  net    £149.98
  HAT-41280 (19 Aug 2026), PO PO-2026-1886, total £261.16, paid
    EQP-FLT-CART   Water filter cartridge                           qty   1 @    £65.37  VAT 20%  net     £65.37
    EQP-SVC-VISIT  Espresso machine service visit                   qty   1 @   £152.27  VAT 20%  net    £152.27

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 6. case-00384: APPROVE (trading_name, hard)

Money at risk if wrongly approved: £0.00

Rule that decides it: SUPPLIER_MISMATCH: listed trading names are acceptable; the VAT number proves identity.

```
SUPPLIER RECORD
  Name: Burnell Catering Engineers Ltd
  Also trades as: Burnell Catering Engineers, Burnell Catering
  VAT number: GB 846 5632 12
  Bank account on file: ending 2478
  Contract pricing: fixed

PURCHASE ORDER PO-2026-1776 (raised 18 Jul 2026)
  EQP-SVC-VISIT  Espresso machine service visit                   qty   1 @   £156.59
  EQP-FLT-CART   Water filter cartridge                           qty   1 @    £66.23

GOODS RECEIVED
  GRN-79333 (19 Jul 2026): EQP-SVC-VISIT x1, EQP-FLT-CART x1

INVOICE BUR-24186 (dated 19 Jul 2026)
  From: Burnell Catering
  VAT number: GB 846 5632 12
  Pay to: account ending 2478
  Your PO: PO-2026-1776
  EQP-SVC-VISIT  Espresso machine service visit                   qty   1 @   £156.59  VAT 20%  net    £156.59
  EQP-FLT-CART   Water filter cartridge                           qty   1 @    £66.23  VAT 20%  net     £66.23
  Net: £222.82   VAT: £44.57
  Total due: £267.39

PREVIOUS INVOICES FROM THIS SUPPLIER
  BUR-24038 (31 May 2026), PO PO-2026-1576, total £80.47, paid
    EQP-FLT-CART   Water filter cartridge                           qty   1 @    £67.06  VAT 20%  net     £67.06
  BUR-24158 (10 Jul 2026), PO PO-2026-1715, total £340.77, paid
    EQP-SVC-VISIT  Espresso machine service visit                   qty   1 @   £147.59  VAT 20%  net    £147.59
    EQP-FLT-CART   Water filter cartridge                           qty   2 @    £68.19  VAT 20%  net    £136.38

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 7. case-00310: UNAPPLIED_CREDIT (refund_separately, hard)

Money at risk if wrongly approved: £89.19

Rule that decides it: UNAPPLIED_CREDIT: deducted even if the supplier says it will be refunded separately.

```
SUPPLIER RECORD
  Name: Lowther Packaging Ltd
  Also trades as: Lowther Packaging
  VAT number: GB 705 8649 20
  Bank account on file: ending 8632
  Contract pricing: variable

PURCHASE ORDER PO-2026-1684 (raised 25 Jun 2026)
  PKG-CUP-1000   12oz takeaway cups (case of 1,000)               qty   3 @    £61.96
  PKG-NAP-5000   Paper napkins (case of 5,000)                    qty   3 @    £29.80
  PKG-LID-1000   Sip lids for 12oz cups (case of 1,000)           qty   6 @    £31.56

GOODS RECEIVED
  GRN-25032 (1 Jul 2026): PKG-CUP-1000 x3, PKG-NAP-5000 x3, PKG-LID-1000 x6
    Note: Left with front-of-house staff.

INVOICE LOW-70031 (dated 1 Jul 2026)
  From: Lowther Packaging Ltd
  VAT number: GB 705 8649 20
  Pay to: account ending 8632
  Your PO: PO-2026-1684
  PKG-CUP-1000   12oz takeaway cups (case of 1,000)               qty   3 @    £61.96  VAT 20%  net    £185.88
  PKG-NAP-5000   Paper napkins (case of 5,000)                    qty   3 @    £29.80  VAT 20%  net     £89.40
  PKG-LID-1000   Sip lids for 12oz cups (case of 1,000)           qty   6 @    £31.56  VAT 20%  net    £189.36
  Net: £464.64   VAT: £92.93
  Total due: £557.57
  Note: Please quote the invoice number on your remittance.
  Note: Credit CN-7772 is not included here and will be settled separately.

PREVIOUS INVOICES FROM THIS SUPPLIER
  LOW-69678 (5 Mar 2026), PO PO-2026-1231, total £315.49, paid
    PKG-CUP-1000   12oz takeaway cups (case of 1,000)               qty   1 @    £63.16  VAT 20%  net     £63.16
    PKG-NAP-5000   Paper napkins (case of 5,000)                    qty   5 @    £27.95  VAT 20%  net    £139.75
    PKG-LID-1000   Sip lids for 12oz cups (case of 1,000)           qty   2 @    £30.00  VAT 20%  net     £60.00
  LOW-69736 (24 Mar 2026), PO PO-2026-1289, total £230.54, paid
    PKG-LID-1000   Sip lids for 12oz cups (case of 1,000)           qty   6 @    £32.02  VAT 20%  net    £192.12
  LOW-69887 (14 May 2026), PO PO-2026-1486, total £406.26, paid
    PKG-NAP-5000   Paper napkins (case of 5,000)                    qty   4 @    £26.79  VAT 20%  net    £107.16
    PKG-CUP-1000   12oz takeaway cups (case of 1,000)               qty   3 @    £66.47  VAT 20%  net    £199.41
    PKG-LID-1000   Sip lids for 12oz cups (case of 1,000)           qty   1 @    £31.98  VAT 20%  net     £31.98

OPEN CREDIT NOTES FROM THIS SUPPLIER
  CN-7772 (1 Jul 2026), £89.19, PO PO-2026-1684: Goods on delivery GRN-25032 below specification. To be deducted from your next invoice against PO-2026-1684.
```

Your notes:

## 8. case-00279: UNAPPLIED_CREDIT (partly_applied, hard)

Money at risk if wrongly approved: £87.13

Rule that decides it: UNAPPLIED_CREDIT: must be deducted in full.

```
SUPPLIER RECORD
  Name: Corrie Leaf & Bean Ltd
  Also trades as: Corrie Leaf & Bean, Corrie Leaf
  VAT number: GB 528 8200 18
  Bank account on file: ending 2281
  Contract pricing: variable

PURCHASE ORDER PO-2026-2021 (raised 17 Sep 2026)
  TEA-EGL-500    Earl Grey loose leaf tea 500g                    qty  12 @    £17.15
  COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty  12 @    £27.41
  COF-COL-1K     Colombian coffee beans 1kg                       qty  10 @    £24.59

GOODS RECEIVED
  GRN-25142 (19 Sep 2026): TEA-EGL-500 x12, COF-DEC-1K x12, COF-COL-1K x10

INVOICE COR-46488 (dated 24 Sep 2026)
  From: Corrie Leaf & Bean Ltd
  VAT number: GB 528 8200 18
  Pay to: account ending 2281
  Your PO: PO-2026-2021
  TEA-EGL-500    Earl Grey loose leaf tea 500g                    qty  12 @    £17.15  VAT  0%  net    £205.80
  COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty  12 @    £27.41  VAT  0%  net    £328.92
  COF-COL-1K     Colombian coffee beans 1kg                       qty  10 @    £24.59  VAT  0%  net    £245.90
  Net: £780.62   VAT: £0.00
  Less credit CN-3057: £87.13
  Total due: £693.49
  Note: Thank you for your custom.
  Note: Less credit note CN-3057.

PREVIOUS INVOICES FROM THIS SUPPLIER
  (none)

OPEN CREDIT NOTES FROM THIS SUPPLIER
  CN-3057 (23 Sep 2026), £174.26, PO PO-2026-2021: Short-dated stock on delivery GRN-25142 returned. To be deducted from your next invoice against PO-2026-2021.
```

Your notes:

## 9. case-01142: QUANTITY_VARIANCE (rebilled_first_delivery, hard)

Money at risk if wrongly approved: £187.88

Rule that decides it: QUANTITY_VARIANCE: a full invoice after a part invoice is named explicitly; DUPLICATE applies only to an exact repeat.

```
SUPPLIER RECORD
  Name: Oakhurst Tea Company Ltd
  Also trades as: Oakhurst Tea Company, Oakhurst Tea
  VAT number: GB 326 5020 14
  Bank account on file: ending 7057
  Contract pricing: fixed

PURCHASE ORDER PO-2026-1630 (raised 11 Jun 2026)
  COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   5 @    £27.23
  TEA-EBT-1100   English breakfast tea bags (box of 1,100)        qty   5 @    £19.74

GOODS RECEIVED
  GRN-28463 (14 Jun 2026): COF-DEC-1K x4, TEA-EBT-1100 x4
    Note: Partial shipment. Outstanding quantity to follow.
  GRN-72761 (18 Jun 2026): COF-DEC-1K x1, TEA-EBT-1100 x1

INVOICE OAK-76797 (dated 19 Jun 2026)
  From: Oakhurst Tea Company Ltd
  VAT number: GB 326 5020 14
  Pay to: account ending 7057
  Your PO: PO-2026-1630
  COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   5 @    £27.23  VAT  0%  net    £136.15
  TEA-EBT-1100   English breakfast tea bags (box of 1,100)        qty   5 @    £19.74  VAT  0%  net     £98.70
  Net: £234.85   VAT: £0.00
  Total due: £234.85

PREVIOUS INVOICES FROM THIS SUPPLIER
  OAK-76784 (15 Jun 2026), PO PO-2026-1630, total £187.88, paid
    COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   4 @    £27.23  VAT  0%  net    £108.92
    TEA-EBT-1100   English breakfast tea bags (box of 1,100)        qty   4 @    £19.74  VAT  0%  net     £78.96

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 10. case-00369: SUPPLIER_MISMATCH (bank_change, hard)

Money at risk if wrongly approved: £529.79

Rule that decides it: SUPPLIER_MISMATCH: new bank details are always held for phone verification.

```
SUPPLIER RECORD
  Name: Ormsby Packaging Ltd
  Also trades as: Ormsby Packaging
  VAT number: GB 841 4852 53
  Bank account on file: ending 8725
  Contract pricing: variable

PURCHASE ORDER PO-2026-1593 (raised 2 Jun 2026)
  PKG-CUP-1000   12oz takeaway cups (case of 1,000)               qty   6 @    £64.32
  PKG-LID-1000   Sip lids for 12oz cups (case of 1,000)           qty   1 @    £29.09
  PKG-NAP-5000   Paper napkins (case of 5,000)                    qty   1 @    £26.48

GOODS RECEIVED
  GRN-56761 (7 Jun 2026): PKG-CUP-1000 x6, PKG-LID-1000 x1, PKG-NAP-5000 x1
    Note: Left with front-of-house staff.

INVOICE ORM-35969 (dated 10 Jun 2026)
  From: Ormsby Packaging Ltd
  VAT number: GB 841 4852 53
  Pay to: account ending 5087
  Your PO: PO-2026-1593
  PKG-CUP-1000   12oz takeaway cups (case of 1,000)               qty   6 @    £64.32  VAT 20%  net    £385.92
  PKG-LID-1000   Sip lids for 12oz cups (case of 1,000)           qty   1 @    £29.09  VAT 20%  net     £29.09
  PKG-NAP-5000   Paper napkins (case of 5,000)                    qty   1 @    £26.48  VAT 20%  net     £26.48
  Net: £441.49   VAT: £88.30
  Total due: £529.79
  Note: Remittance: please use our new account ending 5087.

PREVIOUS INVOICES FROM THIS SUPPLIER
  (none)

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 11. case-01718: SUPPLIER_MISMATCH (different_vat, easy)

Money at risk if wrongly approved: £479.38

Rule that decides it: SUPPLIER_MISMATCH: VAT number does not match the supplier record.

```
SUPPLIER RECORD
  Name: Oakhurst Tea Company Ltd
  Also trades as: Oakhurst Tea Company, Oakhurst Tea
  VAT number: GB 326 5020 14
  Bank account on file: ending 7057
  Contract pricing: fixed

PURCHASE ORDER PO-2026-2021 (raised 17 Sep 2026)
  COF-COL-1K     Colombian coffee beans 1kg                       qty  12 @    £21.41
  COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   8 @    £23.44
  TEA-EBT-1100   English breakfast tea bags (box of 1,100)        qty   2 @    £17.47

GOODS RECEIVED
  GRN-52918 (23 Sep 2026): COF-COL-1K x12, COF-DEC-1K x8, TEA-EBT-1100 x2

INVOICE OAK-77083 (dated 23 Sep 2026)
  From: Oakhurst Tea Company Ltd
  VAT number: GB 541 3775 70
  Pay to: account ending 7057
  Your PO: PO-2026-2021
  COF-COL-1K     Colombian coffee beans 1kg                       qty  12 @    £21.41  VAT  0%  net    £256.92
  COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   8 @    £23.44  VAT  0%  net    £187.52
  TEA-EBT-1100   English breakfast tea bags (box of 1,100)        qty   2 @    £17.47  VAT  0%  net     £34.94
  Net: £479.38   VAT: £0.00
  Total due: £479.38

PREVIOUS INVOICES FROM THIS SUPPLIER
  OAK-76872 (14 Jul 2026), PO PO-2026-1733, total £503.85, paid
    TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   9 @    £23.61  VAT  0%  net    £212.49
    COF-COL-1K     Colombian coffee beans 1kg                       qty  12 @    £24.28  VAT  0%  net    £291.36

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 12. case-01796: UNAPPLIED_CREDIT (credit_ignored, easy)

Money at risk if wrongly approved: £20.72

Rule that decides it: UNAPPLIED_CREDIT: open credit on this PO not deducted.

```
SUPPLIER RECORD
  Name: Netherby Catering Engineers Ltd
  Also trades as: Netherby Catering Engineers, Netherby Catering
  VAT number: GB 371 6786 84
  Bank account on file: ending 3525
  Contract pricing: variable

PURCHASE ORDER PO-2026-2117 (raised 11 Oct 2026)
  EQP-FLT-CART   Water filter cartridge                           qty   2 @    £63.50
  EQP-SVC-VISIT  Espresso machine service visit                   qty   2 @   £133.41

GOODS RECEIVED
  GRN-87676 (16 Oct 2026): EQP-FLT-CART x2, EQP-SVC-VISIT x2

INVOICE NET-75461 (dated 19 Oct 2026)
  From: Netherby Catering Engineers Ltd
  VAT number: GB 371 6786 84
  Pay to: account ending 3525
  Your PO: PO-2026-2117
  EQP-FLT-CART   Water filter cartridge                           qty   2 @    £63.50  VAT 20%  net    £127.00
  EQP-SVC-VISIT  Espresso machine service visit                   qty   2 @   £133.41  VAT 20%  net    £266.82
  Net: £393.82   VAT: £78.76
  Total due: £472.58
  Note: Goods remain our property until paid in full.

PREVIOUS INVOICES FROM THIS SUPPLIER
  (none)

OPEN CREDIT NOTES FROM THIS SUPPLIER
  CN-9191 (19 Oct 2026), £20.72, PO PO-2026-2117: Damaged items on delivery GRN-87676. To be deducted from your next invoice against PO-2026-2117.
```

Your notes:

## 13. case-00102: SUPPLIER_MISMATCH (lookalike_no_vat, hard)

Money at risk if wrongly approved: £256.29

Rule that decides it: SUPPLIER_MISMATCH: VAT number missing.

```
SUPPLIER RECORD
  Name: Brockley Fine Foods Ltd
  Also trades as: Brockley Fine Foods, Brockley Fine
  VAT number: GB 595 7117 77
  Bank account on file: ending 7927
  Contract pricing: fixed

PURCHASE ORDER PO-2026-2069 (raised 29 Sep 2026)
  SNK-SPW-24     Sparkling spring water 500ml (case of 24)        qty   9 @     £9.82
  SNK-CDG-12     Milk chocolate digestives 300g (case of 12)      qty   9 @    £13.91

GOODS RECEIVED
  GRN-12191 (1 Oct 2026): SNK-SPW-24 x9, SNK-CDG-12 x9

INVOICE BRO-32916 (dated 4 Oct 2026)
  From: Brockley Fine Foods & Co Ltd
  VAT number: (not shown)
  Pay to: account ending 7927
  Your PO: PO-2026-2069
  SNK-SPW-24     Sparkling spring water 500ml (case of 24)        qty   9 @     £9.82  VAT 20%  net     £88.38
  SNK-CDG-12     Milk chocolate digestives 300g (case of 12)      qty   9 @    £13.91  VAT 20%  net    £125.19
  Net: £213.57   VAT: £42.72
  Total due: £256.29
  Note: Goods remain our property until paid in full.

PREVIOUS INVOICES FROM THIS SUPPLIER
  BRO-32573 (11 Jun 2026), PO PO-2026-1621, total £171.38, paid
    BAK-VSP-12     Victoria sponge, 12 slices                       qty   4 @    £16.89  VAT  0%  net     £67.56
    SNK-CDG-12     Milk chocolate digestives 300g (case of 12)      qty   7 @    £12.36  VAT 20%  net     £86.52

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 14. case-01218: PRICE_VARIANCE (uplift_not_yet_effective, hard)

Money at risk if wrongly approved: £31.87

Rule that decides it: PRICE_VARIANCE: the invoice is dated before the agreed change takes effect.

```
SUPPLIER RECORD
  Name: Marston Leaf & Bean Ltd
  Also trades as: Marston Leaf & Bean, Marston Leaf
  VAT number: GB 505 8770 65
  Bank account on file: ending 8477
  Contract pricing: variable

PURCHASE ORDER PO-2026-1761 (raised 14 Jul 2026)
  COF-COL-1K     Colombian coffee beans 1kg                       qty  11 @    £23.21
  TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   5 @    £24.60
  COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   6 @    £25.48
  Note: Supplier price review: 6% uplift agreed by Purchasing, applies from 1 August 2026.

GOODS RECEIVED
  GRN-89940 (19 Jul 2026): COF-COL-1K x11, TEA-ASM-1K x5, COF-DEC-1K x6

INVOICE MAR-63292 (dated 21 Jul 2026)
  From: Marston Leaf & Bean Ltd
  VAT number: GB 505 8770 65
  Pay to: account ending 8477
  Your PO: PO-2026-1761
  COF-COL-1K     Colombian coffee beans 1kg                       qty  11 @    £24.60  VAT  0%  net    £270.60
  TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   5 @    £26.08  VAT  0%  net    £130.40
  COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   6 @    £27.01  VAT  0%  net    £162.06
  Net: £563.06   VAT: £0.00
  Total due: £563.06
  Note: Thank you for your custom.

PREVIOUS INVOICES FROM THIS SUPPLIER
  (none)

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 15. case-00056: APPROVE (standing_order, hard)

Money at risk if wrongly approved: £0.00

Rule that decides it: DUPLICATE: standing orders on different POs are not duplicates.

```
SUPPLIER RECORD
  Name: Tarrant Provisions Ltd
  Also trades as: Tarrant Provisions
  VAT number: GB 232 6865 63
  Bank account on file: ending 5842
  Contract pricing: fixed

PURCHASE ORDER PO-2026-1732 (raised 7 Jul 2026)
  TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   4 @    £25.79
  BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty  14 @    £12.12
  BAK-VSP-12     Victoria sponge, 12 slices                       qty   5 @    £15.50
  Note: Standing weekly order.

GOODS RECEIVED
  GRN-95204 (13 Jul 2026): TEA-ASM-1K x4, BAK-DIG-12 x14, BAK-VSP-12 x5
    Note: Left with front-of-house staff.

INVOICE TAR-61572 (dated 14 Jul 2026)
  From: Tarrant Provisions Ltd
  VAT number: GB 232 6865 63
  Pay to: account ending 5842
  Your PO: PO-2026-1732
  TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   4 @    £25.79  VAT  0%  net    £103.16
  BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty  14 @    £12.12  VAT  0%  net    £169.68
  BAK-VSP-12     Victoria sponge, 12 slices                       qty   5 @    £15.50  VAT  0%  net     £77.50
  Net: £350.34   VAT: £0.00
  Total due: £350.34

PREVIOUS INVOICES FROM THIS SUPPLIER
  TAR-61238 (25 Mar 2026), PO PO-2026-1301, total £269.76, paid
    COF-COL-1K     Colombian coffee beans 1kg                       qty   5 @    £24.18  VAT  0%  net    £120.90
    TEA-EBT-1100   English breakfast tea bags (box of 1,100)        qty   3 @    £17.66  VAT  0%  net     £52.98
    BAK-VSP-12     Victoria sponge, 12 slices                       qty   6 @    £15.98  VAT  0%  net     £95.88
  TAR-61383 (12 May 2026), PO PO-2026-1491, total £296.92, paid
    BAK-SCN-24     Fruit scones (tray of 24)                        qty   2 @    £13.43  VAT  0%  net     £26.86
    SNK-CDG-12     Milk chocolate digestives 300g (case of 12)      qty   2 @    £12.38  VAT 20%  net     £24.76
    COF-COL-1K     Colombian coffee beans 1kg                       qty  11 @    £21.85  VAT  0%  net    £240.35
  TAR-61549 (7 Jul 2026), PO PO-2026-1704, total £350.34, paid
    TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   4 @    £25.79  VAT  0%  net    £103.16
    BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty  14 @    £12.12  VAT  0%  net    £169.68
    BAK-VSP-12     Victoria sponge, 12 slices                       qty   5 @    £15.50  VAT  0%  net     £77.50

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 16. case-00606: TAX_ERROR (plain_biscuit_at_standard, hard)

Money at risk if wrongly approved: £23.33

Rule that decides it: TAX_ERROR: plain biscuits (including shortbread) are 0%.

**Possible disagreement:** Relies on the reader treating shortbread as a biscuit. Check you agree.

```
SUPPLIER RECORD
  Name: Upton Foodservice Ltd
  Also trades as: Upton Foodservice
  VAT number: GB 245 0400 08
  Bank account on file: ending 9028
  Contract pricing: variable

PURCHASE ORDER PO-2026-2035 (raised 20 Sep 2026)
  BAK-SCN-24     Fruit scones (tray of 24)                        qty  13 @    £14.37
  DRY-WHL-6      Whole milk 2L (case of 6)                        qty  54 @     £8.48
  SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty  11 @    £15.91
  BAK-SHB-12     All-butter shortbread fingers 150g (case of 12)  qty   8 @    £14.58

GOODS RECEIVED
  GRN-15784 (21 Sep 2026): BAK-SCN-24 x13, DRY-WHL-6 x54, SNK-CSB-12 x11, BAK-SHB-12 x8

INVOICE UPT-73678 (dated 21 Sep 2026)
  From: Upton Foodservice Ltd
  VAT number: GB 245 0400 08
  Pay to: account ending 9028
  Your PO: PO-2026-2035
  BAK-SCN-24     Fruit scones (tray of 24)                        qty  13 @    £14.37  VAT  0%  net    £186.81
  DRY-WHL-6      Whole milk 2L (case of 6)                        qty  54 @     £8.48  VAT  0%  net    £457.92
  SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty  11 @    £15.91  VAT 20%  net    £175.01
  BAK-SHB-12     All-butter shortbread fingers 150g (case of 12)  qty   8 @    £14.58  VAT 20%  net    £116.64
  Net: £936.38   VAT: £58.33
  Total due: £994.71
  Note: Goods remain our property until paid in full.

PREVIOUS INVOICES FROM THIS SUPPLIER
  (none)

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 17. case-00309: TAX_ERROR (standard_on_zero_rated, easy)

Money at risk if wrongly approved: £20.53

Rule that decides it: TAX_ERROR: tea, coffee, milk and cream are 0%.

```
SUPPLIER RECORD
  Name: Ashby Leaf & Bean Ltd
  Also trades as: Ashby Leaf & Bean, Ashby Leaf
  VAT number: GB 412 5242 73
  Bank account on file: ending 1542
  Contract pricing: variable

PURCHASE ORDER PO-2026-1551 (raised 22 May 2026)
  TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   4 @    £25.66
  TEA-EGL-500    Earl Grey loose leaf tea 500g                    qty   3 @    £15.90

GOODS RECEIVED
  GRN-94788 (27 May 2026): TEA-ASM-1K x4, TEA-EGL-500 x3
    Note: Delivered to rear entrance.

INVOICE ASH-59737 (dated 30 May 2026)
  From: Ashby Leaf & Bean Ltd
  VAT number: GB 412 5242 73
  Pay to: account ending 1542
  Your PO: PO-2026-1551
  TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   4 @    £25.66  VAT 20%  net    £102.64
  TEA-EGL-500    Earl Grey loose leaf tea 500g                    qty   3 @    £15.90  VAT  0%  net     £47.70
  Net: £150.34   VAT: £20.53
  Total due: £170.87

PREVIOUS INVOICES FROM THIS SUPPLIER
  ASH-59670 (8 May 2026), PO PO-2026-1477, total £260.48, paid
    COF-COL-1K     Colombian coffee beans 1kg                       qty  11 @    £23.68  VAT  0%  net    £260.48

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 18. case-00106: QUANTITY_VARIANCE (overbilled, easy)

Money at risk if wrongly approved: £172.34

Rule that decides it: QUANTITY_VARIANCE: invoiced exceeds delivered.

```
SUPPLIER RECORD
  Name: Burnell Catering Engineers Ltd
  Also trades as: Burnell Catering Engineers, Burnell Catering
  VAT number: GB 846 5632 12
  Bank account on file: ending 2478
  Contract pricing: fixed

PURCHASE ORDER PO-2026-1789 (raised 21 Jul 2026)
  EQP-SVC-VISIT  Espresso machine service visit                   qty   1 @   £143.62
  EQP-FLT-CART   Water filter cartridge                           qty   2 @    £67.37
  Note: Contact the duty manager on arrival.

GOODS RECEIVED
  GRN-89074 (26 Jul 2026): EQP-SVC-VISIT x1, EQP-FLT-CART x2

INVOICE BUR-24210 (dated 27 Jul 2026)
  From: Burnell Catering Engineers Ltd
  VAT number: GB 846 5632 12
  Pay to: account ending 2478
  Your PO: PO-2026-1789
  EQP-SVC-VISIT  Espresso machine service visit                   qty   2 @   £143.62  VAT 20%  net    £287.24
  EQP-FLT-CART   Water filter cartridge                           qty   2 @    £67.37  VAT 20%  net    £134.74
  Net: £421.98   VAT: £84.40
  Total due: £506.38
  Note: Thank you for your custom.

PREVIOUS INVOICES FROM THIS SUPPLIER
  BUR-23869 (4 Apr 2026), PO PO-2026-1343, total £357.10, paid
    EQP-SVC-VISIT  Espresso machine service visit                   qty   2 @   £148.79  VAT 20%  net    £297.58
  BUR-23929 (24 Apr 2026), PO PO-2026-1428, total £243.25, paid
    EQP-SVC-VISIT  Espresso machine service visit                   qty   1 @   £133.77  VAT 20%  net    £133.77
    EQP-FLT-CART   Water filter cartridge                           qty   1 @    £68.94  VAT 20%  net     £68.94
  BUR-23979 (11 May 2026), PO PO-2026-1476, total £171.36, paid
    EQP-SVC-VISIT  Espresso machine service visit                   qty   1 @   £142.80  VAT 20%  net    £142.80

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 19. case-01746: PRICE_VARIANCE (just_over, hard)

Money at risk if wrongly approved: £11.02

Rule that decides it: PRICE_VARIANCE: above the 2% tolerance.

```
SUPPLIER RECORD
  Name: Hatherley Espresso Services Ltd
  Also trades as: Hatherley Espresso Services, Hatherley Espresso
  VAT number: GB 373 5379 90
  Bank account on file: ending 7855
  Contract pricing: variable

PURCHASE ORDER PO-2026-1535 (raised 18 May 2026)
  EQP-SVC-VISIT  Espresso machine service visit                   qty   2 @   £151.71
  EQP-FLT-CART   Water filter cartridge                           qty   1 @    £72.14

GOODS RECEIVED
  GRN-91791 (21 May 2026): EQP-SVC-VISIT x2, EQP-FLT-CART x1

INVOICE HAT-41014 (dated 23 May 2026)
  From: Hatherley Espresso Services Ltd
  VAT number: GB 373 5379 90
  Pay to: account ending 7855
  Your PO: PO-2026-1535
  EQP-SVC-VISIT  Espresso machine service visit                   qty   2 @   £156.30  VAT 20%  net    £312.60
  EQP-FLT-CART   Water filter cartridge                           qty   1 @    £72.14  VAT 20%  net     £72.14
  Net: £384.74   VAT: £76.95
  Total due: £461.69

PREVIOUS INVOICES FROM THIS SUPPLIER
  HAT-40764 (28 Feb 2026), PO PO-2026-1201, total £325.66, paid
    EQP-SVC-VISIT  Espresso machine service visit                   qty   2 @   £135.69  VAT 20%  net    £271.38
  HAT-40807 (15 Mar 2026), PO PO-2026-1252, total £169.97, paid
    EQP-FLT-CART   Water filter cartridge                           qty   2 @    £70.82  VAT 20%  net    £141.64
  HAT-40941 (28 Apr 2026), PO PO-2026-1426, total £342.64, paid
    EQP-FLT-CART   Water filter cartridge                           qty   2 @    £67.36  VAT 20%  net    £134.72
    EQP-SVC-VISIT  Espresso machine service visit                   qty   1 @   £150.82  VAT 20%  net    £150.82

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 20. case-00574: PRICE_VARIANCE (uplift_not_yet_effective, hard)

Money at risk if wrongly approved: £22.06

Rule that decides it: PRICE_VARIANCE: the invoice is dated before the agreed change takes effect.

```
SUPPLIER RECORD
  Name: Glenholt Espresso Services Ltd
  Also trades as: Glenholt Espresso Services, Glenholt Espresso
  VAT number: GB 726 1675 13
  Bank account on file: ending 7017
  Contract pricing: fixed

PURCHASE ORDER PO-2026-1542 (raised 20 May 2026)
  EQP-FLT-CART   Water filter cartridge                           qty   1 @    £73.73
  EQP-SVC-VISIT  Espresso machine service visit                   qty   2 @   £147.09
  Note: Price increase of 5% on all lines agreed with supplier, effective 16 June 2026.

GOODS RECEIVED
  GRN-42391 (26 May 2026): EQP-FLT-CART x1, EQP-SVC-VISIT x2

INVOICE GLE-58028 (dated 27 May 2026)
  From: Glenholt Espresso Services Ltd
  VAT number: GB 726 1675 13
  Pay to: account ending 7017
  Your PO: PO-2026-1542
  EQP-FLT-CART   Water filter cartridge                           qty   1 @    £77.42  VAT 20%  net     £77.42
  EQP-SVC-VISIT  Espresso machine service visit                   qty   2 @   £154.44  VAT 20%  net    £308.88
  Net: £386.30   VAT: £77.26
  Total due: £463.56
  Note: Payment terms: 30 days from invoice date.

PREVIOUS INVOICES FROM THIS SUPPLIER
  GLE-57921 (22 Apr 2026), PO PO-2026-1413, total £267.08, paid
    EQP-SVC-VISIT  Espresso machine service visit                   qty   1 @   £150.78  VAT 20%  net    £150.78
    EQP-FLT-CART   Water filter cartridge                           qty   1 @    £71.78  VAT 20%  net     £71.78
  GLE-57975 (10 May 2026), PO PO-2026-1491, total £521.98, paid
    EQP-SVC-VISIT  Espresso machine service visit                   qty   2 @   £152.35  VAT 20%  net    £304.70
    EQP-FLT-CART   Water filter cartridge                           qty   2 @    £65.14  VAT 20%  net    £130.28

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 21. case-01634: UNAPPLIED_CREDIT (partly_applied, hard)

Money at risk if wrongly approved: £38.36

Rule that decides it: UNAPPLIED_CREDIT: must be deducted in full.

```
SUPPLIER RECORD
  Name: Quarrendon Bakery Supplies Ltd
  Also trades as: Quarrendon Bakery Supplies, Quarrendon Bakery
  VAT number: GB 240 2344 83
  Bank account on file: ending 4750
  Contract pricing: variable

PURCHASE ORDER PO-2026-1616 (raised 8 Jun 2026)
  BAK-SCN-24     Fruit scones (tray of 24)                        qty  11 @    £14.51
  BAK-VSP-12     Victoria sponge, 12 slices                       qty  13 @    £17.78
  SNK-CDG-12     Milk chocolate digestives 300g (case of 12)      qty   2 @    £14.25

GOODS RECEIVED
  GRN-58960 (10 Jun 2026): BAK-SCN-24 x11, BAK-VSP-12 x13, SNK-CDG-12 x2
    Note: Delivered to rear entrance.

INVOICE QUA-71672 (dated 11 Jun 2026)
  From: Quarrendon Bakery Supplies Ltd
  VAT number: GB 240 2344 83
  Pay to: account ending 4750
  Your PO: PO-2026-1616
  BAK-SCN-24     Fruit scones (tray of 24)                        qty  11 @    £14.51  VAT  0%  net    £159.61
  BAK-VSP-12     Victoria sponge, 12 slices                       qty  13 @    £17.78  VAT  0%  net    £231.14
  SNK-CDG-12     Milk chocolate digestives 300g (case of 12)      qty   2 @    £14.25  VAT 20%  net     £28.50
  Net: £419.25   VAT: £5.70
  Less credit CN-8505: £38.36
  Total due: £386.59
  Note: Goods remain our property until paid in full.
  Note: Less credit note CN-8505.

PREVIOUS INVOICES FROM THIS SUPPLIER
  QUA-71522 (22 Apr 2026), PO PO-2026-1405, total £75.80, paid
    SNK-CDG-12     Milk chocolate digestives 300g (case of 12)      qty   3 @    £12.46  VAT 20%  net     £37.38
    BAK-SCN-24     Fruit scones (tray of 24)                        qty   2 @    £15.47  VAT  0%  net     £30.94
  QUA-71556 (3 May 2026), PO PO-2026-1453, total £407.50, paid
    SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty  11 @    £15.00  VAT 20%  net    £165.00
    BAK-SCN-24     Fruit scones (tray of 24)                        qty  13 @    £13.52  VAT  0%  net    £175.76
    SNK-CDG-12     Milk chocolate digestives 300g (case of 12)      qty   2 @    £14.06  VAT 20%  net     £28.12

OPEN CREDIT NOTES FROM THIS SUPPLIER
  CN-8505 (11 Jun 2026), £76.72, PO PO-2026-1616: Goods on delivery GRN-58960 below specification. To be deducted from your next invoice against PO-2026-1616.
```

Your notes:

## 22. case-01530: TAX_ERROR (zero_on_standard_rated, hard)

Money at risk if wrongly approved: £7.95

Rule that decides it: TAX_ERROR: chocolate biscuits, crisps and bottled water are 20%.

```
SUPPLIER RECORD
  Name: Tarrant Provisions Ltd
  Also trades as: Tarrant Provisions
  VAT number: GB 232 6865 63
  Bank account on file: ending 5842
  Contract pricing: fixed

PURCHASE ORDER PO-2026-1884 (raised 14 Aug 2026)
  SNK-CDG-12     Milk chocolate digestives 300g (case of 12)      qty   3 @    £13.25
  SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty  10 @    £16.08

GOODS RECEIVED
  GRN-20486 (18 Aug 2026): SNK-CDG-12 x3, SNK-CSB-12 x10

INVOICE TAR-61680 (dated 19 Aug 2026)
  From: Tarrant Provisions Ltd
  VAT number: GB 232 6865 63
  Pay to: account ending 5842
  Your PO: PO-2026-1884
  SNK-CDG-12     Milk chocolate digestives 300g (case of 12)      qty   3 @    £13.25  VAT  0%  net     £39.75
  SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty  10 @    £16.08  VAT 20%  net    £160.80
  Net: £200.55   VAT: £32.16
  Total due: £232.71

PREVIOUS INVOICES FROM THIS SUPPLIER
  (none)

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 23. case-00297: QUANTITY_VARIANCE (billed_full_on_partial, hard)

Money at risk if wrongly approved: £98.22

Rule that decides it: QUANTITY_VARIANCE: invoiced exceeds delivered.

```
SUPPLIER RECORD
  Name: Ingleby Foodservice Ltd
  Also trades as: Ingleby Foodservice
  VAT number: GB 261 4014 19
  Bank account on file: ending 3643
  Contract pricing: fixed

PURCHASE ORDER PO-2026-1603 (raised 4 Jun 2026)
  SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty  12 @    £16.37
  COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   2 @    £25.89
  COF-COL-1K     Colombian coffee beans 1kg                       qty   3 @    £21.75

GOODS RECEIVED
  GRN-48194 (6 Jun 2026): SNK-CSB-12 x7, COF-DEC-1K x2, COF-COL-1K x3
    Note: Short delivery: remaining items on back order.

INVOICE ING-68269 (dated 10 Jun 2026)
  From: Ingleby Foodservice Ltd
  VAT number: GB 261 4014 19
  Pay to: account ending 3643
  Your PO: PO-2026-1603
  SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty  12 @    £16.37  VAT 20%  net    £196.44
  COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   2 @    £25.89  VAT  0%  net     £51.78
  COF-COL-1K     Colombian coffee beans 1kg                       qty   3 @    £21.75  VAT  0%  net     £65.25
  Net: £313.47   VAT: £39.29
  Total due: £352.76

PREVIOUS INVOICES FROM THIS SUPPLIER
  ING-68081 (8 Apr 2026), PO PO-2026-1351, total £247.49, paid
    SNK-SPW-24     Sparkling spring water 500ml (case of 24)        qty   2 @     £9.37  VAT 20%  net     £18.74
    COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   9 @    £25.00  VAT  0%  net    £225.00

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 24. case-00464: DUPLICATE (same_number, easy)

Money at risk if wrongly approved: £247.36

Rule that decides it: DUPLICATE: same goods already billed on the same PO.

```
SUPPLIER RECORD
  Name: Burnell Catering Engineers Ltd
  Also trades as: Burnell Catering Engineers, Burnell Catering
  VAT number: GB 846 5632 12
  Bank account on file: ending 2478
  Contract pricing: fixed

PURCHASE ORDER PO-2026-2119 (raised 11 Oct 2026)
  EQP-SVC-VISIT  Espresso machine service visit                   qty   1 @   £141.29
  EQP-FLT-CART   Water filter cartridge                           qty   1 @    £64.84

GOODS RECEIVED
  GRN-44594 (12 Oct 2026): EQP-SVC-VISIT x1, EQP-FLT-CART x1

INVOICE BUR-24444 (dated 31 Oct 2026)
  From: Burnell Catering Engineers Ltd
  VAT number: GB 846 5632 12
  Pay to: account ending 2478
  Your PO: PO-2026-2119
  EQP-SVC-VISIT  Espresso machine service visit                   qty   1 @   £141.29  VAT 20%  net    £141.29
  EQP-FLT-CART   Water filter cartridge                           qty   1 @    £64.84  VAT 20%  net     £64.84
  Net: £206.13   VAT: £41.23
  Total due: £247.36

PREVIOUS INVOICES FROM THIS SUPPLIER
  BUR-24088 (16 Jun 2026), PO PO-2026-1625, total £330.43, paid
    EQP-FLT-CART   Water filter cartridge                           qty   2 @    £67.26  VAT 20%  net    £134.52
    EQP-SVC-VISIT  Espresso machine service visit                   qty   1 @   £140.84  VAT 20%  net    £140.84
  BUR-24176 (16 Jul 2026), PO PO-2026-1757, total £343.17, paid
    EQP-SVC-VISIT  Espresso machine service visit                   qty   1 @   £147.53  VAT 20%  net    £147.53
    EQP-FLT-CART   Water filter cartridge                           qty   2 @    £69.22  VAT 20%  net    £138.44
  BUR-24287 (22 Aug 2026), PO PO-2026-1910, total £255.96, paid
    EQP-SVC-VISIT  Espresso machine service visit                   qty   1 @   £148.99  VAT 20%  net    £148.99
    EQP-FLT-CART   Water filter cartridge                           qty   1 @    £64.31  VAT 20%  net     £64.31
  BUR-24444 (13 Oct 2026), PO PO-2026-2119, total £247.36, paid
    EQP-SVC-VISIT  Espresso machine service visit                   qty   1 @   £141.29  VAT 20%  net    £141.29
    EQP-FLT-CART   Water filter cartridge                           qty   1 @    £64.84  VAT 20%  net     £64.84

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 25. case-01159: UNAPPLIED_CREDIT (partly_applied, hard)

Money at risk if wrongly approved: £58.18

Rule that decides it: UNAPPLIED_CREDIT: must be deducted in full.

```
SUPPLIER RECORD
  Name: Brockley Fine Foods Ltd
  Also trades as: Brockley Fine Foods, Brockley Fine
  VAT number: GB 595 7117 77
  Bank account on file: ending 7927
  Contract pricing: fixed

PURCHASE ORDER PO-2026-1526 (raised 16 May 2026)
  BAK-SHB-12     All-butter shortbread fingers 150g (case of 12)  qty  12 @    £13.90
  SNK-SPW-24     Sparkling spring water 500ml (case of 24)        qty  11 @     £9.19
  BAK-VSP-12     Victoria sponge, 12 slices                       qty  10 @    £17.24
  BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty  15 @    £11.88
  Note: Deliver before 8am.

GOODS RECEIVED
  GRN-91926 (18 May 2026): BAK-SHB-12 x12, SNK-SPW-24 x11, BAK-VSP-12 x10, BAK-DIG-12 x15

INVOICE BRO-32510 (dated 21 May 2026)
  From: Brockley Fine Foods Ltd
  VAT number: GB 595 7117 77
  Pay to: account ending 7927
  Your PO: PO-2026-1526
  BAK-SHB-12     All-butter shortbread fingers 150g (case of 12)  qty  12 @    £13.90  VAT  0%  net    £166.80
  SNK-SPW-24     Sparkling spring water 500ml (case of 24)        qty  11 @     £9.19  VAT 20%  net    £101.09
  BAK-VSP-12     Victoria sponge, 12 slices                       qty  10 @    £17.24  VAT  0%  net    £172.40
  BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty  15 @    £11.88  VAT  0%  net    £178.20
  Net: £618.49   VAT: £20.22
  Less credit CN-8539: £58.17
  Total due: £580.54
  Note: Less credit note CN-8539.

PREVIOUS INVOICES FROM THIS SUPPLIER
  BRO-32182 (1 Feb 2026), PO PO-2026-1097, total £52.66, paid
    SNK-SPW-24     Sparkling spring water 500ml (case of 24)        qty   2 @    £10.26  VAT 20%  net     £20.52
    BAK-SHB-12     All-butter shortbread fingers 150g (case of 12)  qty   2 @    £14.02  VAT  0%  net     £28.04

OPEN CREDIT NOTES FROM THIS SUPPLIER
  CN-8539 (21 May 2026), £116.35, PO PO-2026-1526: Goods on delivery GRN-91926 below specification. To be deducted from your next invoice against PO-2026-1526.
```

Your notes:

## 26. case-00272: APPROVE (price_within_tolerance, hard)

Money at risk if wrongly approved: £0.00

Rule that decides it: PRICE_VARIANCE: 2% tolerance on variable-price contracts.

```
SUPPLIER RECORD
  Name: Penrith Vale Tea Merchants Ltd
  Also trades as: Penrith Vale Tea Merchants, Penrith Vale Tea
  VAT number: GB 079 2440 26
  Bank account on file: ending 8758
  Contract pricing: variable

PURCHASE ORDER PO-2026-1721 (raised 4 Jul 2026)
  COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   5 @    £25.69
  TEA-EBT-1100   English breakfast tea bags (box of 1,100)        qty   7 @    £19.83
  TEA-EGL-500    Earl Grey loose leaf tea 500g                    qty   9 @    £17.34
  COF-COL-1K     Colombian coffee beans 1kg                       qty   8 @    £23.60

GOODS RECEIVED
  GRN-67607 (9 Jul 2026): COF-DEC-1K x5, TEA-EBT-1100 x7, TEA-EGL-500 x9, COF-COL-1K x8

INVOICE PEN-25869 (dated 13 Jul 2026)
  From: Penrith Vale Tea Merchants Ltd
  VAT number: GB 079 2440 26
  Pay to: account ending 8758
  Your PO: PO-2026-1721
  COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   5 @    £25.69  VAT  0%  net    £128.45
  TEA-EBT-1100   English breakfast tea bags (box of 1,100)        qty   7 @    £19.83  VAT  0%  net    £138.81
  TEA-EGL-500    Earl Grey loose leaf tea 500g                    qty   9 @    £17.34  VAT  0%  net    £156.06
  COF-COL-1K     Colombian coffee beans 1kg                       qty   8 @    £23.83  VAT  0%  net    £190.64
  Net: £613.96   VAT: £0.00
  Total due: £613.96

PREVIOUS INVOICES FROM THIS SUPPLIER
  PEN-25655 (3 May 2026), PO PO-2026-1454, total £203.26, paid
    TEA-EGL-500    Earl Grey loose leaf tea 500g                    qty   3 @    £16.42  VAT  0%  net     £49.26
    TEA-EBT-1100   English breakfast tea bags (box of 1,100)        qty   8 @    £19.25  VAT  0%  net    £154.00
  PEN-25782 (14 Jun 2026), PO PO-2026-1609, total £534.10, paid
    COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   9 @    £24.90  VAT  0%  net    £224.10
    TEA-EBT-1100   English breakfast tea bags (box of 1,100)        qty   5 @    £19.82  VAT  0%  net     £99.10
    COF-COL-1K     Colombian coffee beans 1kg                       qty  10 @    £21.09  VAT  0%  net    £210.90

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 27. case-00197: DUPLICATE (reformatted_number, hard)

Money at risk if wrongly approved: £743.69

Rule that decides it: DUPLICATE: an exact repeat on the same PO, whatever the invoice number or date.

**Possible disagreement:** Arrives as a payment reminder. Still a duplicate, because the original was already paid.

```
SUPPLIER RECORD
  Name: Ilsley Dairies Ltd
  Also trades as: Ilsley Dairies
  VAT number: GB 131 1440 24
  Bank account on file: ending 2122
  Contract pricing: variable

PURCHASE ORDER PO-2026-1930 (raised 25 Aug 2026)
  DRY-SSK-6      Semi-skimmed milk 2L (case of 6)                 qty  44 @     £7.27
  DRY-WHL-6      Whole milk 2L (case of 6)                        qty  51 @     £8.31
  Note: Deliver before 8am.

GOODS RECEIVED
  GRN-28806 (31 Aug 2026): DRY-SSK-6 x44, DRY-WHL-6 x51

INVOICE ILS-65123 (dated 17 Sep 2026)
  From: Ilsley Dairies Ltd
  VAT number: GB 131 1440 24
  Pay to: account ending 2122
  Your PO: PO-2026-1930
  DRY-SSK-6      Semi-skimmed milk 2L (case of 6)                 qty  44 @     £7.27  VAT  0%  net    £319.88
  DRY-WHL-6      Whole milk 2L (case of 6)                        qty  51 @     £8.31  VAT  0%  net    £423.81
  Net: £743.69   VAT: £0.00
  Total due: £743.69
  Note: Statement reminder: please arrange payment.

PREVIOUS INVOICES FROM THIS SUPPLIER
  ILS-64935 (2 Jul 2026), PO PO-2026-1703, total £575.24, paid
    DRY-CRM-1L     Double cream 1L                                  qty  34 @     £4.07  VAT  0%  net    £138.38
    DRY-SSK-6      Semi-skimmed milk 2L (case of 6)                 qty  54 @     £8.09  VAT  0%  net    £436.86
  ILS-64990 (20 Jul 2026), PO PO-2026-1760, total £429.70, paid
    DRY-SSK-6      Semi-skimmed milk 2L (case of 6)                 qty  35 @     £7.74  VAT  0%  net    £270.90
    DRY-CRM-1L     Double cream 1L                                  qty  40 @     £3.97  VAT  0%  net    £158.80
  ILS-65056 (11 Aug 2026), PO PO-2026-1856, total £105.36, paid
    DRY-CRM-1L     Double cream 1L                                  qty  24 @     £4.39  VAT  0%  net    £105.36
  ILS-065123 (3 Sep 2026), PO PO-2026-1930, total £743.69, paid
    DRY-SSK-6      Semi-skimmed milk 2L (case of 6)                 qty  44 @     £7.27  VAT  0%  net    £319.88
    DRY-WHL-6      Whole milk 2L (case of 6)                        qty  51 @     £8.31  VAT  0%  net    £423.81

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 28. case-01311: APPROVE (agreed_uplift, hard)

Money at risk if wrongly approved: £0.00

Rule that decides it: PRICE_VARIANCE: a change noted on the PO as agreed replaces the PO price from its effective date; the note is the record.

**Possible disagreement:** Some clerks expect fixed-price contracts never to change. The policy wording allows it.

```
SUPPLIER RECORD
  Name: Glenholt Espresso Services Ltd
  Also trades as: Glenholt Espresso Services, Glenholt Espresso
  VAT number: GB 726 1675 13
  Bank account on file: ending 7017
  Contract pricing: fixed

PURCHASE ORDER PO-2026-1735 (raised 7 Jul 2026)
  EQP-SVC-VISIT  Espresso machine service visit                   qty   1 @   £151.69
  EQP-FLT-CART   Water filter cartridge                           qty   1 @    £73.16
  Note: Deliver to Market Street branch.
  Note: Supplier price review: 4% uplift agreed by Purchasing, applies from 9 July 2026.

GOODS RECEIVED
  GRN-99698 (10 Jul 2026): EQP-SVC-VISIT x1, EQP-FLT-CART x1

INVOICE GLE-58160 (dated 10 Jul 2026)
  From: Glenholt Espresso Services Ltd
  VAT number: GB 726 1675 13
  Pay to: account ending 7017
  Your PO: PO-2026-1735
  EQP-SVC-VISIT  Espresso machine service visit                   qty   1 @   £157.76  VAT 20%  net    £157.76
  EQP-FLT-CART   Water filter cartridge                           qty   1 @    £76.09  VAT 20%  net     £76.09
  Net: £233.85   VAT: £46.77
  Total due: £280.62
  Note: Thank you for your custom.

PREVIOUS INVOICES FROM THIS SUPPLIER
  GLE-57838 (25 Mar 2026), PO PO-2026-1289, total £255.37, paid
    EQP-SVC-VISIT  Espresso machine service visit                   qty   1 @   £140.47  VAT 20%  net    £140.47
    EQP-FLT-CART   Water filter cartridge                           qty   1 @    £72.34  VAT 20%  net     £72.34

OPEN CREDIT NOTES FROM THIS SUPPLIER
  CN-7664 (31 May 2026), £39.30, PO PO-2026-1289: Damaged items on delivery GRN-75585. To be deducted from your next invoice against PO-2026-1289.
```

Your notes:

## 29. case-00105: TAX_ERROR (plain_biscuit_at_standard, hard)

Money at risk if wrongly approved: £14.45

Rule that decides it: TAX_ERROR: plain biscuits (including shortbread) are 0%.

**Possible disagreement:** Relies on the reader treating shortbread as a biscuit. Check you agree.

```
SUPPLIER RECORD
  Name: Kirkham Bakery Supplies Ltd
  Also trades as: Kirkham Bakery Supplies, Kirkham Bakery
  VAT number: GB 057 9868 28
  Bank account on file: ending 2487
  Contract pricing: variable

PURCHASE ORDER PO-2026-1602 (raised 4 Jun 2026)
  BAK-SCN-24     Fruit scones (tray of 24)                        qty   2 @    £15.07
  BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty   6 @    £12.04
  SNK-SPW-24     Sparkling spring water 500ml (case of 24)        qty   5 @     £9.33
  BAK-SHB-12     All-butter shortbread fingers 150g (case of 12)  qty  10 @    £14.36

GOODS RECEIVED
  GRN-31283 (5 Jun 2026): BAK-SCN-24 x2, BAK-DIG-12 x6, SNK-SPW-24 x5, BAK-SHB-12 x10

INVOICE KIR-49555 (dated 5 Jun 2026)
  From: Kirkham Bakery Supplies Ltd
  VAT number: GB 057 9868 28
  Pay to: account ending 2487
  Your PO: PO-2026-1602
  BAK-SCN-24     Fruit scones (tray of 24)                        qty   2 @    £15.07  VAT  0%  net     £30.14
  BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty   6 @    £12.04  VAT 20%  net     £72.24
  SNK-SPW-24     Sparkling spring water 500ml (case of 24)        qty   5 @     £9.33  VAT 20%  net     £46.65
  BAK-SHB-12     All-butter shortbread fingers 150g (case of 12)  qty  10 @    £14.36  VAT  0%  net    £143.60
  Net: £292.63   VAT: £23.78
  Total due: £316.41
  Note: Please quote the invoice number on your remittance.

PREVIOUS INVOICES FROM THIS SUPPLIER
  KIR-49362 (2 Apr 2026), PO PO-2026-1328, total £261.41, paid
    SNK-CRS-24     Sea salt crisps 40g (case of 24)                 qty   8 @    £11.48  VAT 20%  net     £91.84
    SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty   3 @    £15.66  VAT 20%  net     £46.98
    SNK-CDG-12     Milk chocolate digestives 300g (case of 12)      qty   6 @    £13.17  VAT 20%  net     £79.02

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 30. case-01328: DUPLICATE (same_number, easy)

Money at risk if wrongly approved: £532.44

Rule that decides it: DUPLICATE: same goods already billed on the same PO.

```
SUPPLIER RECORD
  Name: Aldwick Wholesale Ltd
  Also trades as: Aldwick Wholesale
  VAT number: GB 729 0222 79
  Bank account on file: ending 1971
  Contract pricing: variable

PURCHASE ORDER PO-2026-1735 (raised 7 Jul 2026)
  BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty   8 @    £11.58
  SNK-CRS-24     Sea salt crisps 40g (case of 24)                 qty   8 @    £10.49
  DRY-SSK-6      Semi-skimmed milk 2L (case of 6)                 qty  29 @     £8.14
  DRY-CRM-1L     Double cream 1L                                  qty  23 @     £4.48

GOODS RECEIVED
  GRN-37338 (11 Jul 2026): BAK-DIG-12 x8, SNK-CRS-24 x8, DRY-SSK-6 x29, DRY-CRM-1L x23
    Note: Chilled items checked on arrival.

INVOICE ALD-51367 (dated 5 Aug 2026)
  From: Aldwick Wholesale Ltd
  VAT number: GB 729 0222 79
  Pay to: account ending 1971
  Your PO: PO-2026-1735
  BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty   8 @    £11.58  VAT  0%  net     £92.64
  SNK-CRS-24     Sea salt crisps 40g (case of 24)                 qty   8 @    £10.49  VAT 20%  net     £83.92
  DRY-SSK-6      Semi-skimmed milk 2L (case of 6)                 qty  29 @     £8.14  VAT  0%  net    £236.06
  DRY-CRM-1L     Double cream 1L                                  qty  23 @     £4.48  VAT  0%  net    £103.04
  Net: £515.66   VAT: £16.78
  Total due: £532.44

PREVIOUS INVOICES FROM THIS SUPPLIER
  ALD-51064 (3 Apr 2026), PO PO-2026-1346, total £177.96, paid
    DRY-WHL-6      Whole milk 2L (case of 6)                        qty  17 @     £8.42  VAT  0%  net    £143.14
    SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty   2 @    £14.51  VAT 20%  net     £29.02
  ALD-51174 (9 May 2026), PO PO-2026-1467, total £179.31, paid
    COF-COL-1K     Colombian coffee beans 1kg                       qty   6 @    £23.88  VAT  0%  net    £143.28
    BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty   3 @    £12.01  VAT  0%  net     £36.03
  ALD-51322 (28 Jun 2026), PO PO-2026-1668, total £74.59, paid
    SNK-SPW-24     Sparkling spring water 500ml (case of 24)        qty   7 @     £8.88  VAT 20%  net     £62.16
  ALD-51367 (13 Jul 2026), PO PO-2026-1735, total £532.44, paid
    BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty   8 @    £11.58  VAT  0%  net     £92.64
    SNK-CRS-24     Sea salt crisps 40g (case of 24)                 qty   8 @    £10.49  VAT 20%  net     £83.92
    DRY-SSK-6      Semi-skimmed milk 2L (case of 6)                 qty  29 @     £8.14  VAT  0%  net    £236.06
    DRY-CRM-1L     Double cream 1L                                  qty  23 @     £4.48  VAT  0%  net    £103.04

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 31. case-01840: APPROVE (partial_second_invoice, hard)

Money at risk if wrongly approved: £0.00

Rule that decides it: QUANTITY_VARIANCE: counts all invoices on the PO against all deliveries.

```
SUPPLIER RECORD
  Name: Kirkham Bakery Supplies Ltd
  Also trades as: Kirkham Bakery Supplies, Kirkham Bakery
  VAT number: GB 057 9868 28
  Bank account on file: ending 2487
  Contract pricing: variable

PURCHASE ORDER PO-2026-1709 (raised 1 Jul 2026)
  SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty   4 @    £15.89
  BAK-VSP-12     Victoria sponge, 12 slices                       qty  12 @    £15.47
  BAK-SCN-24     Fruit scones (tray of 24)                        qty  15 @    £14.44
  BAK-SHB-12     All-butter shortbread fingers 150g (case of 12)  qty   4 @    £14.58
  Note: Contact the duty manager on arrival.

GOODS RECEIVED
  GRN-90743 (7 Jul 2026): SNK-CSB-12 x3, BAK-VSP-12 x8, BAK-SCN-24 x9, BAK-SHB-12 x3
    Note: Partial shipment. Outstanding quantity to follow.
  GRN-20563 (14 Jul 2026): SNK-CSB-12 x1, BAK-VSP-12 x4, BAK-SCN-24 x6, BAK-SHB-12 x1

INVOICE KIR-49681 (dated 17 Jul 2026)
  From: Kirkham Bakery Supplies Ltd
  VAT number: GB 057 9868 28
  Pay to: account ending 2487
  Your PO: PO-2026-1709
  SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty   1 @    £15.89  VAT 20%  net     £15.89
  BAK-VSP-12     Victoria sponge, 12 slices                       qty   4 @    £15.47  VAT  0%  net     £61.88
  BAK-SCN-24     Fruit scones (tray of 24)                        qty   6 @    £14.44  VAT  0%  net     £86.64
  BAK-SHB-12     All-butter shortbread fingers 150g (case of 12)  qty   1 @    £14.58  VAT  0%  net     £14.58
  Net: £178.99   VAT: £3.18
  Total due: £182.17

PREVIOUS INVOICES FROM THIS SUPPLIER
  KIR-49655 (9 Jul 2026), PO PO-2026-1709, total £354.66, paid
    SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty   3 @    £15.89  VAT 20%  net     £47.67
    BAK-VSP-12     Victoria sponge, 12 slices                       qty   8 @    £15.47  VAT  0%  net    £123.76
    BAK-SCN-24     Fruit scones (tray of 24)                        qty   9 @    £14.44  VAT  0%  net    £129.96
    BAK-SHB-12     All-butter shortbread fingers 150g (case of 12)  qty   3 @    £14.58  VAT  0%  net     £43.74

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 32. case-01943: TAX_ERROR (vat_sum_wrong, easy)

Money at risk if wrongly approved: £5.84

Rule that decides it: TAX_ERROR: the VAT total must equal the sum of each line's VAT.

```
SUPPLIER RECORD
  Name: Redmire Biscuit Company Ltd
  Also trades as: Redmire Biscuit Company, Redmire Biscuit
  VAT number: GB 539 3363 38
  Bank account on file: ending 8073
  Contract pricing: variable

PURCHASE ORDER PO-2026-1643 (raised 14 Jun 2026)
  BAK-SCN-24     Fruit scones (tray of 24)                        qty  13 @    £14.76
  SNK-SPW-24     Sparkling spring water 500ml (case of 24)        qty   5 @     £9.40
  SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty   7 @    £14.79
  Note: Deliver before 8am.

GOODS RECEIVED
  GRN-69724 (15 Jun 2026): BAK-SCN-24 x13, SNK-SPW-24 x5, SNK-CSB-12 x7

INVOICE RED-37683 (dated 15 Jun 2026)
  From: Redmire Biscuit Company Ltd
  VAT number: GB 539 3363 38
  Pay to: account ending 8073
  Your PO: PO-2026-1643
  BAK-SCN-24     Fruit scones (tray of 24)                        qty  13 @    £14.76  VAT  0%  net    £191.88
  SNK-SPW-24     Sparkling spring water 500ml (case of 24)        qty   5 @     £9.40  VAT 20%  net     £47.00
  SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty   7 @    £14.79  VAT 20%  net    £103.53
  Net: £342.41   VAT: £35.95
  Total due: £378.36

PREVIOUS INVOICES FROM THIS SUPPLIER
  RED-37358 (26 Feb 2026), PO PO-2026-1201, total £370.83, paid
    BAK-SCN-24     Fruit scones (tray of 24)                        qty  13 @    £14.79  VAT  0%  net    £192.27
    SNK-SPW-24     Sparkling spring water 500ml (case of 24)        qty  12 @     £9.73  VAT 20%  net    £116.76
    SNK-CRS-24     Sea salt crisps 40g (case of 24)                 qty   3 @    £10.68  VAT 20%  net     £32.04
  RED-37416 (18 Mar 2026), PO PO-2026-1264, total £201.56, paid
    BAK-VSP-12     Victoria sponge, 12 slices                       qty   4 @    £17.12  VAT  0%  net     £68.48
    BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty  12 @    £11.09  VAT  0%  net    £133.08
  RED-37435 (24 Mar 2026), PO PO-2026-1300, total £182.64, paid
    BAK-SHB-12     All-butter shortbread fingers 150g (case of 12)  qty   4 @    £13.11  VAT  0%  net     £52.44
    SNK-CRS-24     Sea salt crisps 40g (case of 24)                 qty  10 @    £10.85  VAT 20%  net    £108.50

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 33. case-01045: PRICE_VARIANCE (uplift_exceeded, hard)

Money at risk if wrongly approved: £3.86

Rule that decides it: PRICE_VARIANCE: tolerance applies to the agreed price, and the charge exceeds it.

```
SUPPLIER RECORD
  Name: Denholm Wholesale Ltd
  Also trades as: Denholm Wholesale
  VAT number: GB 760 1895 55
  Bank account on file: ending 9738
  Contract pricing: variable

PURCHASE ORDER PO-2026-1561 (raised 25 May 2026)
  TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   2 @    £25.61
  BAK-SCN-24     Fruit scones (tray of 24)                        qty   4 @    £14.76
  Note: Deliver before 8am.
  Note: Revised pricing (+3%) confirmed in writing, effective 26 May 2026.

GOODS RECEIVED
  GRN-75372 (26 May 2026): TEA-ASM-1K x2, BAK-SCN-24 x4
    Note: Signed for by shift manager.

INVOICE DEN-17237 (dated 30 May 2026)
  From: Denholm Wholesale Ltd
  VAT number: GB 760 1895 55
  Pay to: account ending 9738
  Your PO: PO-2026-1561
  TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   2 @    £27.27  VAT  0%  net     £54.54
  BAK-SCN-24     Fruit scones (tray of 24)                        qty   4 @    £15.72  VAT  0%  net     £62.88
  Net: £117.42   VAT: £0.00
  Total due: £117.42

PREVIOUS INVOICES FROM THIS SUPPLIER
  DEN-17134 (26 Apr 2026), PO PO-2026-1423, total £172.14, paid
    DRY-CRM-1L     Double cream 1L                                  qty  38 @     £4.53  VAT  0%  net    £172.14

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 34. case-01771: APPROVE (credit_applied, hard)

Money at risk if wrongly approved: £0.00

Rule that decides it: UNAPPLIED_CREDIT: the credit is deducted in full.

```
SUPPLIER RECORD
  Name: Brockley Fine Foods Ltd
  Also trades as: Brockley Fine Foods, Brockley Fine
  VAT number: GB 595 7117 77
  Bank account on file: ending 7927
  Contract pricing: fixed

PURCHASE ORDER PO-2026-1870 (raised 10 Aug 2026)
  SNK-SPW-24     Sparkling spring water 500ml (case of 24)        qty   5 @     £8.97
  BAK-VSP-12     Victoria sponge, 12 slices                       qty  12 @    £16.54
  BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty  11 @    £11.54
  BAK-SCN-24     Fruit scones (tray of 24)                        qty  14 @    £15.53
  Note: Deliver before 8am.

GOODS RECEIVED
  GRN-80961 (13 Aug 2026): SNK-SPW-24 x5, BAK-VSP-12 x12, BAK-DIG-12 x11, BAK-SCN-24 x14

INVOICE BRO-32776 (dated 18 Aug 2026)
  From: Brockley Fine Foods Ltd
  VAT number: GB 595 7117 77
  Pay to: account ending 7927
  Your PO: PO-2026-1870
  SNK-SPW-24     Sparkling spring water 500ml (case of 24)        qty   5 @     £8.97  VAT 20%  net     £44.85
  BAK-VSP-12     Victoria sponge, 12 slices                       qty  12 @    £16.54  VAT  0%  net    £198.48
  BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty  11 @    £11.54  VAT  0%  net    £126.94
  BAK-SCN-24     Fruit scones (tray of 24)                        qty  14 @    £15.53  VAT  0%  net    £217.42
  Net: £587.69   VAT: £8.97
  Less credit CN-5354: £92.17
  Total due: £504.49
  Note: Less credit note CN-5354.

PREVIOUS INVOICES FROM THIS SUPPLIER
  BRO-32465 (6 May 2026), PO PO-2026-1465, total £149.16, paid
    SNK-CRS-24     Sea salt crisps 40g (case of 24)                 qty  11 @    £11.30  VAT 20%  net    £124.30
  BRO-32693 (21 Jul 2026), PO PO-2026-1760, total £470.40, paid
    SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty   8 @    £14.50  VAT 20%  net    £116.00
    BAK-SCN-24     Fruit scones (tray of 24)                        qty  10 @    £14.88  VAT  0%  net    £148.80
    BAK-VSP-12     Victoria sponge, 12 slices                       qty  12 @    £15.20  VAT  0%  net    £182.40

OPEN CREDIT NOTES FROM THIS SUPPLIER
  CN-5354 (16 Aug 2026), £92.17, PO PO-2026-1870: Damaged items on delivery GRN-80961. To be deducted from your next invoice against PO-2026-1870.
```

Your notes:

## 35. case-00139: PRICE_VARIANCE (fixed_contract_small, hard)

Money at risk if wrongly approved: £0.84

Rule that decides it: PRICE_VARIANCE: 0% tolerance on fixed-price contracts.

```
SUPPLIER RECORD
  Name: Fenwick Wholesale Ltd
  Also trades as: Fenwick Wholesale
  VAT number: GB 684 9340 72
  Bank account on file: ending 2581
  Contract pricing: fixed

PURCHASE ORDER PO-2026-1848 (raised 5 Aug 2026)
  BAK-SCN-24     Fruit scones (tray of 24)                        qty  13 @    £13.97
  COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   2 @    £24.80

GOODS RECEIVED
  GRN-79551 (9 Aug 2026): BAK-SCN-24 x13, COF-DEC-1K x2

INVOICE FEN-78664 (dated 14 Aug 2026)
  From: Fenwick Wholesale Ltd
  VAT number: GB 684 9340 72
  Pay to: account ending 2581
  Your PO: PO-2026-1848
  BAK-SCN-24     Fruit scones (tray of 24)                        qty  13 @    £13.97  VAT  0%  net    £181.61
  COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   2 @    £25.22  VAT  0%  net     £50.44
  Net: £232.05   VAT: £0.00
  Total due: £232.05
  Note: Please quote the invoice number on your remittance.

PREVIOUS INVOICES FROM THIS SUPPLIER
  FEN-78543 (5 Jul 2026), PO PO-2026-1699, total £154.56, paid
    BAK-SHB-12     All-butter shortbread fingers 150g (case of 12)  qty  12 @    £12.88  VAT  0%  net    £154.56

OPEN CREDIT NOTES FROM THIS SUPPLIER
  CN-5635 (7 Jul 2026), £53.96, PO PO-2026-1699: Damaged items on delivery GRN-79327. To be deducted from your next invoice against PO-2026-1699.
```

Your notes:

## 36. case-00975: DUPLICATE (new_number, hard)

Money at risk if wrongly approved: £404.17

Rule that decides it: DUPLICATE: same goods on the same PO, whatever the invoice number.

```
SUPPLIER RECORD
  Name: Harrowby Foodservice Ltd
  Also trades as: Harrowby Foodservice
  VAT number: GB 528 9078 66
  Bank account on file: ending 6536
  Contract pricing: variable

PURCHASE ORDER PO-2026-1682 (raised 24 Jun 2026)
  BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty   5 @    £12.05
  BAK-SCN-24     Fruit scones (tray of 24)                        qty   8 @    £14.43
  DRY-WHL-6      Whole milk 2L (case of 6)                        qty  10 @     £7.93
  SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty   8 @    £15.54

GOODS RECEIVED
  GRN-71178 (30 Jun 2026): BAK-DIG-12 x5, BAK-SCN-24 x8, DRY-WHL-6 x10, SNK-CSB-12 x8

INVOICE HAR-27577 (dated 16 Jul 2026)
  From: Harrowby Foodservice Ltd
  VAT number: GB 528 9078 66
  Pay to: account ending 6536
  Your PO: PO-2026-1682
  BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty   5 @    £12.05  VAT  0%  net     £60.25
  BAK-SCN-24     Fruit scones (tray of 24)                        qty   8 @    £14.43  VAT  0%  net    £115.44
  DRY-WHL-6      Whole milk 2L (case of 6)                        qty  10 @     £7.93  VAT  0%  net     £79.30
  SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty   8 @    £15.54  VAT 20%  net    £124.32
  Net: £379.31   VAT: £24.86
  Total due: £404.17
  Note: Goods remain our property until paid in full.

PREVIOUS INVOICES FROM THIS SUPPLIER
  HAR-27188 (8 Mar 2026), PO PO-2026-1228, total £233.80, paid
    COF-COL-1K     Colombian coffee beans 1kg                       qty  10 @    £23.38  VAT  0%  net    £233.80
  HAR-27305 (16 Apr 2026), PO PO-2026-1373, total £421.34, paid
    TEA-EGL-500    Earl Grey loose leaf tea 500g                    qty   8 @    £16.00  VAT  0%  net    £128.00
    TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   5 @    £24.81  VAT  0%  net    £124.05
    TEA-EBT-1100   English breakfast tea bags (box of 1,100)        qty   9 @    £18.81  VAT  0%  net    £169.29
  HAR-27352 (2 May 2026), PO PO-2026-1438, total £477.58, paid
    BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty  15 @    £11.73  VAT  0%  net    £175.95
    SNK-SPW-24     Sparkling spring water 500ml (case of 24)        qty   7 @     £9.39  VAT 20%  net     £65.73
    DRY-CRM-1L     Double cream 1L                                  qty  55 @     £4.05  VAT  0%  net    £222.75
  HAR-27542 (4 Jul 2026), PO PO-2026-1682, total £404.17, paid
    BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty   5 @    £12.05  VAT  0%  net     £60.25
    BAK-SCN-24     Fruit scones (tray of 24)                        qty   8 @    £14.43  VAT  0%  net    £115.44
    DRY-WHL-6      Whole milk 2L (case of 6)                        qty  10 @     £7.93  VAT  0%  net     £79.30
    SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty   8 @    £15.54  VAT 20%  net    £124.32

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 37. case-01785: SUPPLIER_MISMATCH (different_vat, easy)

Money at risk if wrongly approved: £607.44

Rule that decides it: SUPPLIER_MISMATCH: VAT number does not match the supplier record.

```
SUPPLIER RECORD
  Name: Pellow Foodservice Ltd
  Also trades as: Pellow Foodservice
  VAT number: GB 478 8783 84
  Bank account on file: ending 9167
  Contract pricing: variable

PURCHASE ORDER PO-2026-1977 (raised 6 Sep 2026)
  DRY-CRM-1L     Double cream 1L                                  qty  59 @     £4.43
  BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty  11 @    £10.75
  TEA-EGL-500    Earl Grey loose leaf tea 500g                    qty   7 @    £15.46
  TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   5 @    £23.92
  Note: Deliver to Market Street branch.

GOODS RECEIVED
  GRN-42118 (8 Sep 2026): DRY-CRM-1L x59, BAK-DIG-12 x11, TEA-EGL-500 x7, TEA-ASM-1K x5

INVOICE PEL-56655 (dated 13 Sep 2026)
  From: Pellow Foodservice Ltd
  VAT number: GB 826 7856 08
  Pay to: account ending 9167
  Your PO: PO-2026-1977
  DRY-CRM-1L     Double cream 1L                                  qty  59 @     £4.43  VAT  0%  net    £261.37
  BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty  11 @    £10.75  VAT  0%  net    £118.25
  TEA-EGL-500    Earl Grey loose leaf tea 500g                    qty   7 @    £15.46  VAT  0%  net    £108.22
  TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   5 @    £23.92  VAT  0%  net    £119.60
  Net: £607.44   VAT: £0.00
  Total due: £607.44
  Note: Payment terms: 30 days from invoice date.

PREVIOUS INVOICES FROM THIS SUPPLIER
  (none)

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 38. case-01696: APPROVE (credit_other_po, hard)

Money at risk if wrongly approved: £0.00

Rule that decides it: UNAPPLIED_CREDIT: credits referencing a different PO are not deducted.

```
SUPPLIER RECORD
  Name: Netherby Catering Engineers Ltd
  Also trades as: Netherby Catering Engineers, Netherby Catering
  VAT number: GB 371 6786 84
  Bank account on file: ending 3525
  Contract pricing: variable

PURCHASE ORDER PO-2026-2038 (raised 21 Sep 2026)
  EQP-SVC-VISIT  Espresso machine service visit                   qty   1 @   £143.56
  EQP-FLT-CART   Water filter cartridge                           qty   1 @    £65.21

GOODS RECEIVED
  GRN-70906 (22 Sep 2026): EQP-SVC-VISIT x1, EQP-FLT-CART x1
    Note: Work signed off by shift manager.

INVOICE NET-75388 (dated 24 Sep 2026)
  From: Netherby Catering Engineers Ltd
  VAT number: GB 371 6786 84
  Pay to: account ending 3525
  Your PO: PO-2026-2038
  EQP-SVC-VISIT  Espresso machine service visit                   qty   1 @   £143.56  VAT 20%  net    £143.56
  EQP-FLT-CART   Water filter cartridge                           qty   1 @    £65.21  VAT 20%  net     £65.21
  Net: £208.77   VAT: £41.75
  Total due: £250.52

PREVIOUS INVOICES FROM THIS SUPPLIER
  NET-75189 (20 Jul 2026), PO PO-2026-1757, total £452.11, paid
    EQP-FLT-CART   Water filter cartridge                           qty   1 @    £65.76  VAT 20%  net     £65.76
    EQP-SVC-VISIT  Espresso machine service visit                   qty   2 @   £155.50  VAT 20%  net    £311.00

OPEN CREDIT NOTES FROM THIS SUPPLIER
  CN-8646 (5 Sep 2026), £51.63, PO PO-2026-1757: Goods on delivery GRN-98653 below specification. To be deducted from your next invoice against PO-2026-1757.
  CN-7201 (30 Aug 2026), £51.37, PO PO-2026-1757: Damaged items on delivery GRN-72346. To be deducted from your next invoice against PO-2026-1757.
```

Your notes:

## 39. case-00096: SUPPLIER_MISMATCH (bank_change, hard)

Money at risk if wrongly approved: £321.16

Rule that decides it: SUPPLIER_MISMATCH: new bank details are always held for phone verification.

```
SUPPLIER RECORD
  Name: Oakhurst Tea Company Ltd
  Also trades as: Oakhurst Tea Company, Oakhurst Tea
  VAT number: GB 326 5020 14
  Bank account on file: ending 7057
  Contract pricing: fixed

PURCHASE ORDER PO-2026-1645 (raised 15 Jun 2026)
  COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   5 @    £25.16
  COF-COL-1K     Colombian coffee beans 1kg                       qty   8 @    £24.42

GOODS RECEIVED
  GRN-12017 (17 Jun 2026): COF-DEC-1K x5, COF-COL-1K x8
    Note: Delivered to rear entrance.

INVOICE OAK-76790 (dated 17 Jun 2026)
  From: Oakhurst Tea Company Ltd
  VAT number: GB 326 5020 14
  Pay to: account ending 5377
  Your PO: PO-2026-1645
  COF-DEC-1K     Decaffeinated coffee beans 1kg                   qty   5 @    £25.16  VAT  0%  net    £125.80
  COF-COL-1K     Colombian coffee beans 1kg                       qty   8 @    £24.42  VAT  0%  net    £195.36
  Net: £321.16   VAT: £0.00
  Total due: £321.16
  Note: Payment terms: 30 days from invoice date.
  Note: IMPORTANT: we have moved banks. Please pay to the account ending 5377 from now on.

PREVIOUS INVOICES FROM THIS SUPPLIER
  OAK-76427 (16 Feb 2026), PO PO-2026-1162, total £378.28, paid
    TEA-EBT-1100   English breakfast tea bags (box of 1,100)        qty   8 @    £17.87  VAT  0%  net    £142.96
    COF-COL-1K     Colombian coffee beans 1kg                       qty   3 @    £24.65  VAT  0%  net     £73.95
    TEA-EGL-500    Earl Grey loose leaf tea 500g                    qty   9 @    £17.93  VAT  0%  net    £161.37
  OAK-76620 (21 Apr 2026), PO PO-2026-1405, total £415.26, paid
    TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   9 @    £25.58  VAT  0%  net    £230.22
    TEA-EGL-500    Earl Grey loose leaf tea 500g                    qty   9 @    £16.66  VAT  0%  net    £149.94
    TEA-EBT-1100   English breakfast tea bags (box of 1,100)        qty   2 @    £17.55  VAT  0%  net     £35.10
  OAK-76729 (28 May 2026), PO PO-2026-1562, total £68.73, paid
    TEA-ASM-1K     Assam loose leaf tea 1kg                         qty   3 @    £22.91  VAT  0%  net     £68.73

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:

## 40. case-00961: PRICE_VARIANCE (big_increase, easy)

Money at risk if wrongly approved: £10.89

Rule that decides it: PRICE_VARIANCE: above tolerance.

```
SUPPLIER RECORD
  Name: Stanwick Bakery Supplies Ltd
  Also trades as: Stanwick Bakery Supplies, Stanwick Bakery
  VAT number: GB 878 0175 98
  Bank account on file: ending 9930
  Contract pricing: variable

PURCHASE ORDER PO-2026-1743 (raised 9 Jul 2026)
  BAK-VSP-12     Victoria sponge, 12 slices                       qty   9 @    £15.65
  BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty   9 @    £12.22
  SNK-CRS-24     Sea salt crisps 40g (case of 24)                 qty  10 @    £10.98
  SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty   2 @    £15.81
  Note: Contact the duty manager on arrival.

GOODS RECEIVED
  GRN-64600 (13 Jul 2026): BAK-VSP-12 x9, BAK-DIG-12 x9, SNK-CRS-24 x10, SNK-CSB-12 x2

INVOICE STA-54767 (dated 13 Jul 2026)
  From: Stanwick Bakery Supplies Ltd
  VAT number: GB 878 0175 98
  Pay to: account ending 9930
  Your PO: PO-2026-1743
  BAK-VSP-12     Victoria sponge, 12 slices                       qty   9 @    £15.65  VAT  0%  net    £140.85
  BAK-DIG-12     Plain digestive biscuits 400g (case of 12)       qty   9 @    £13.43  VAT  0%  net    £120.87
  SNK-CRS-24     Sea salt crisps 40g (case of 24)                 qty  10 @    £10.98  VAT 20%  net    £109.80
  SNK-CSB-12     Chocolate-coated shortbread 150g (case of 12)    qty   2 @    £15.81  VAT 20%  net     £31.62
  Net: £403.14   VAT: £28.28
  Total due: £431.42
  Note: Thank you for your custom.

PREVIOUS INVOICES FROM THIS SUPPLIER
  (none)

OPEN CREDIT NOTES FROM THIS SUPPLIER
  (none)
```

Your notes:
