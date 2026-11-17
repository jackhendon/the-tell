# Independent blind review by Codex

Codex (OpenAI) labelled the 40 cases in `review_blind.md` without seeing our labels, rules
or scenario names, working only from that file. Its table is reproduced unedited below.
The comparison with our labels, and what changed as a result, is in `review_findings.md`.

| # | Outcome | Other defensible outcome (or none) | Why / notes |
|---|---|---|---|
| 1 | APPROVE | PRICE_VARIANCE | The PO records a 6% uplift effective before the invoice date, and the invoiced prices reflect it after rounding. A strict reading could require separate evidence that the change was *agreed in writing*, which the PO note does not explicitly establish. |
| 2 | TAX_ERROR | none | Milk is charged 20% VAT instead of 0%. |
| 3 | UNAPPLIED_CREDIT | none | Only £11.61 of the £23.22 credit for this PO is deducted. The credit predates the PO it references, which is unrealistic. |
| 4 | QUANTITY_VARIANCE | none | Six Earl Grey units are invoiced; four were received. |
| 5 | SUPPLIER_MISMATCH | none | The invoice bank account ends 6701; the supplier record says 4249. The change notice does not remove the hold. |
| 6 | APPROVE | none | The quantities, fixed prices, VAT and supplier details match. The similar earlier purchase used a different PO. |
| 7 | TAX_ERROR | none | English breakfast tea is charged 20% VAT instead of 0%. The open credit references another PO. |
| 8 | TAX_ERROR | none | Double cream is charged 20% VAT instead of 0%. |
| 9 | APPROVE | none | The invoice uses a listed trading name, and the other checks pass. |
| 10 | QUANTITY_VARIANCE | none | This invoice plus the earlier invoice exceeds the quantities received on the PO. The invoices have different quantities, so they do not meet the duplicate definition. |
| 11 | UNAPPLIED_CREDIT | none | The £42.92 credit for this PO is omitted despite the supplier's separate-settlement note. The credit predates the PO it references. |
| 12 | APPROVE | none | Supplier, quantities, prices and VAT match. |
| 13 | DUPLICATE | none | An earlier invoice bills the same items, quantities and prices on this PO; cumulative invoicing also exceeds receipts. The earlier invoice predates the PO and delivery, which is unrealistic. The credit belongs to another PO. |
| 14 | UNAPPLIED_CREDIT | none | The £25.65 credit references this PO and is not deducted. It predates the PO, despite describing a previous delivery. |
| 15 | APPROVE | none | The napkin price is about 0.75% above the PO price, within the variable-price 2% tolerance. |
| 16 | SUPPLIER_MISMATCH | none | The invoice omits the VAT number. Its company name also differs from the recorded name and trading names. |
| 17 | APPROVE | none | The invoice uses an accepted trading name; the other checks pass. |
| 18 | APPROVE | none | The open credit references a different PO. The invoice otherwise matches. |
| 19 | PRICE_VARIANCE | none | Shortbread is £15.15 per unit against £12.98 on a variable-price PO, well beyond 2%. |
| 20 | UNAPPLIED_CREDIT | none | Only £11.37 of the £22.75 credit is deducted. The credit predates the PO it references. |
| 21 | TAX_ERROR | none | Plain digestive biscuits are charged 20% VAT instead of 0%. |
| 22 | DUPLICATE | none | The earlier paid invoice bills the same goods on the same PO, even though its invoice number is shown in lowercase. Cumulative invoicing also exceeds receipts. |
| 23 | QUANTITY_VARIANCE | none | Two filter cartridges are invoiced; one was received. |
| 24 | PRICE_VARIANCE | none | Semi-skimmed milk is £7.24 against £7.00 on a variable-price PO, above the 2% tolerance. |
| 25 | SUPPLIER_MISMATCH | none | The invoice VAT number differs from the supplier record. |
| 26 | PRICE_VARIANCE | none | The 6% uplift takes effect after the invoice date, so the higher prices exceed the fixed PO prices. This PO number also appears for a different supplier in case 10, an unrealistic cross-case detail. |
| 27 | DUPLICATE | none | An earlier paid invoice bills identical goods on this PO; cumulative invoicing also exceeds receipts. The earlier invoice predates the PO and delivery. |
| 28 | TAX_ERROR | none | Chocolate-coated shortbread is charged 0% VAT instead of 20%. |
| 29 | QUANTITY_VARIANCE | none | Five boxes of English breakfast tea are invoiced; three were received. |
| 30 | APPROVE | none | Supplier, quantities, fixed prices and VAT match. |
| 31 | DUPLICATE | none | The earlier paid invoice bills identical goods on this PO; cumulative invoicing also exceeds receipts. The earlier invoice predates the PO and delivery. |
| 32 | APPROVE | none | This and the earlier partial invoice together match the quantities received across both GRNs. |
| 33 | APPROVE | none | The identical standing order was billed against a different PO, which the policy expressly excludes from duplicates. |
| 34 | UNAPPLIED_CREDIT | none | The £36.88 credit for this PO is omitted. Its description refers to a previous invoice on the PO, but none is listed. |
| 35 | TAX_ERROR | none | All lines are zero-rated, yet the invoice adds £1.15 VAT. |
| 36 | PRICE_VARIANCE | none | Even after the recorded 3% increase takes effect, both invoiced unit prices are higher than the revised fixed prices. |
| 37 | APPROVE | none | Supplier, quantities, fixed prices and VAT match. |
| 38 | APPROVE | none | The full £59.75 credit is deducted. The credit predates the PO it references, which is unrealistic. |
| 39 | PRICE_VARIANCE | none | Scones are £15.81 against £15.54 on a fixed-price PO. This PO number also appears for a different supplier in case 40. |
| 40 | PRICE_VARIANCE | none | The service visit is £147.41 against £145.91 on a fixed-price PO. This PO number also appears for a different supplier in case 39. |
