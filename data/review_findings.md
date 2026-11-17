# Label review: findings

## Why a review was needed

Every label comes from construction and is re-derived by an oracle. Both were written from
the same reading of the policy, so they would agree even where the policy is ambiguous.
If a label could sensibly go another way, the model's "mistakes" on those cases would
measure an unclear policy rather than the model's judgement. Only an independent reader
can catch that.

## Round 1: blind review by Codex (OpenAI), 40 cases

Codex labelled the cases from `review_blind.md`, which contains the policy and the
documents only: no labels, rules, scenario names or case IDs, in shuffled order. It was
run outside the repo so it could not read the answers. Its table is in `review_codex.md`.

**Agreement: 40 of 40 labels.** It named another defensible outcome for 1 case.

| Finding | Cases | Verdict | Action |
|---|---|---|---|
| The policy required price changes "agreed in writing", but the PO note did not always say "in writing", so PRICE_VARIANCE was arguable | 1 | Policy ambiguity | Policy now says the note on the PO is the record of the agreement |
| Credit notes on this PO were dated before the PO existed, some citing a "previous invoice" that did not exist | 3, 11, 14, 20, 34, 38 | Generator bug | Credits on this PO are now dated between its delivery and the invoice, and cite that delivery. Test added |
| Duplicate "earlier" invoices were dated before the PO and the delivery | 13, 27, 31 | Generator bug | The original is now dated after delivery; the copy arrives later. Test added |
| The same PO number appears in different cases for different suppliers | 10/26, 39/40 | Accepted | Each case is an independent scenario and the model sees one at a time, so this cannot affect results |

## A side effect we caught while fixing

The credit-note fix first gave credits on this PO different wording from credits on other
POs ("your invoice" and a delivery number, versus "your next invoice" and no delivery
number). A model could have learned that wording instead of checking the PO number.
Both now use identical phrasing, so only the PO number tells them apart.

## What 40 out of 40 does and does not show

- It supports the labels: an independent frontier model, reading only the policy and the
  documents, reached the same answer every time.
- It does not show the cases are hard enough. If frontier models rarely err on this task,
  the Claude comparison (step 5) will have few mistakes to predict. The 4B open model is
  expected to err far more often; step 3 measures that and tunes difficulty if needed.

## Round 2: owner review of the flagged cases

The project owner (not a finance specialist) reviewed the cases marked "Possible
disagreement" in `review_sample.md`.

| Case | Scenario | Owner's view | Outcome |
|---|---|---|---|
| 9 | Full invoice after a part invoice | Read it as a DUPLICATE: part of the bill repeats a paid invoice | Policy clarified (below) |
| 16 | Plain shortbread charged 20% VAT | Fine: shortbread is a biscuit in British usage | Label confirmed |
| 28 | Agreed price rise on a fixed-price contract | Fine: the policy wording allows it (noted as case 26, taken as a typo for 28, the only case with this flag) | Label confirmed |
| 27 | Duplicate arriving as a payment reminder | Fine: a reminder for a paid invoice is redundant and should be held | Label confirmed |

**Case 9.** Codex agreed with our label; the owner did not. Either reading leads to a hold,
because paying would pay for the first delivery twice, but the experiment needs one right
answer. The decision follows standard accounts payable practice. Invoices are checked by a
three-way match (purchase order, goods received, invoice), and this invoice fails it on
quantity: 9 units invoiced in total against 5 received. "Duplicate" in AP practice means
the same invoice submitted twice, which duplicate checks find by matching invoice number,
amount and date; this invoice would not trigger them. The label stays QUANTITY_VARIANCE,
and the policy now says so explicitly: a full invoice after a part invoice is a quantity
variance, and DUPLICATE applies only to an exact repeat.

## Safeguard against any remaining ambiguity

Results will be scored at two levels: the exact label, and approve versus hold. Every
disagreement found in review was between two reasons for holding, never between approve
and hold. If the probe's result holds at both levels, residual label ambiguity cannot be
what drives it.
