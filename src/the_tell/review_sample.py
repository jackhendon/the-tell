"""Writes a human review sample: one case per scenario, plus random extras.

This replaces hand-labelling every case. The labels come from construction and are
checked by the oracle; what a human checks is whether the cases look realistic and
whether the label is what a sensible AP clerk would also choose.

Run:  uv run python -m the_tell.review_sample --n 40
"""

import argparse
import random
from pathlib import Path

from the_tell.domain import fmt_money
from the_tell.generate import SCENARIOS, generate_cases
from the_tell.policy import POLICY_TEXT
from the_tell.render import render_case

# The policy wording that forces each scenario's label, and, where a reasonable person
# might still disagree, why. Reviewing against this is the real check on the labels:
# the oracle only proves the generator matches the same reading of the policy.
RULES = {
    "clean": ("Nothing in the policy applies.", None),
    "price_within_tolerance": ("PRICE_VARIANCE: 2% tolerance on variable-price contracts.", None),
    "agreed_uplift": ("PRICE_VARIANCE: an agreed change recorded on the PO replaces the PO price from its effective date.",
                      "Some clerks expect fixed-price contracts never to change. The policy wording allows it."),
    "partial_second_invoice": ("QUANTITY_VARIANCE: counts all invoices on the PO against all deliveries.", None),
    "standing_order": ("DUPLICATE: standing orders on different POs are not duplicates.", None),
    "trading_name": ("SUPPLIER_MISMATCH: listed trading names are acceptable; the VAT number proves identity.", None),
    "credit_applied": ("UNAPPLIED_CREDIT: the credit is deducted in full.", None),
    "credit_other_po": ("UNAPPLIED_CREDIT: credits referencing a different PO are not deducted.", None),
    "mixed_vat": ("TAX_ERROR: VAT table, chocolate-covered biscuits 20%, plain biscuits 0%.", None),
    "big_increase": ("PRICE_VARIANCE: above tolerance.", None),
    "just_over": ("PRICE_VARIANCE: above the 2% tolerance.", None),
    "fixed_contract_small": ("PRICE_VARIANCE: 0% tolerance on fixed-price contracts.", None),
    "uplift_exceeded": ("PRICE_VARIANCE: tolerance applies to the agreed price, and the charge exceeds it.", None),
    "uplift_not_yet_effective": ("PRICE_VARIANCE: the invoice is dated before the agreed change takes effect.", None),
    "overbilled": ("QUANTITY_VARIANCE: invoiced exceeds delivered.", None),
    "billed_full_on_partial": ("QUANTITY_VARIANCE: invoiced exceeds delivered.", None),
    "rebilled_first_delivery": ("QUANTITY_VARIANCE: across all invoices on the PO, invoiced exceeds delivered.",
                                "Part of this bill repeats an earlier invoice, so a clerk might call it a DUPLICATE. "
                                "The policy defines DUPLICATE as the same items, quantities and prices, which this is not."),
    "same_number": ("DUPLICATE: same goods already billed on the same PO.", None),
    "reformatted_number": ("DUPLICATE: same goods on the same PO, whatever the invoice number or date.",
                           "Arrives as a payment reminder. Still a duplicate, because the original was already paid."),
    "new_number": ("DUPLICATE: same goods on the same PO, whatever the invoice number.", None),
    "standard_on_zero_rated": ("TAX_ERROR: tea, coffee, milk and cream are 0%.", None),
    "zero_on_standard_rated": ("TAX_ERROR: chocolate biscuits, crisps and bottled water are 20%.", None),
    "plain_biscuit_at_standard": ("TAX_ERROR: plain biscuits (including shortbread) are 0%.",
                                  "Relies on the reader treating shortbread as a biscuit. Check you agree."),
    "vat_sum_wrong": ("TAX_ERROR: the VAT total must equal the sum of each line's VAT.", None),
    "different_vat": ("SUPPLIER_MISMATCH: VAT number does not match the supplier record.", None),
    "bank_change": ("SUPPLIER_MISMATCH: new bank details are always held for phone verification.", None),
    "lookalike_no_vat": ("SUPPLIER_MISMATCH: VAT number missing.", None),
    "credit_ignored": ("UNAPPLIED_CREDIT: open credit on this PO not deducted.", None),
    "refund_separately": ("UNAPPLIED_CREDIT: deducted even if the supplier says it will be refunded separately.", None),
    "partly_applied": ("UNAPPLIED_CREDIT: must be deducted in full.", None),
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out", type=Path, default=Path("data/review_sample.md"))
    args = ap.parse_args()

    cases = generate_cases(2000, args.seed)
    rng = random.Random(args.seed)

    picked = []
    for s in SCENARIOS:
        matches = [c for c in cases if c.scenario == s.name and c.label == s.label]
        if matches:
            picked.append(rng.choice(matches))
    rest = [c for c in cases if c not in picked]
    picked += rng.sample(rest, max(0, args.n - len(picked)))
    rng.shuffle(picked)  # otherwise case order follows the scenario list and hints at the answer

    out = [
        "# Review sample",
        "",
        f"{len(picked)} cases: one from each of the {len(SCENARIOS)} scenarios, then random extras.",
        "For each case, check two things and note anything off:",
        "",
        "1. **Realism.** Would a real AP clerk see documents like this?",
        "2. **Forced label.** Does the quoted policy rule force this answer, with no other",
        "   sensible reading? This matters most. If a sensible reader could choose differently,",
        "   the model's 'mistakes' on such cases measure an unclear policy, not judgement.",
        "",
        "Cases marked **Possible disagreement** are where I think a reasonable person might",
        "pause. Decide whether the policy wording settles it, or needs changing.",
        "",
        "<details><summary>AP policy given to the model</summary>",
        "",
        "```",
        POLICY_TEXT,
        "```",
        "</details>",
        "",
    ]
    for i, c in enumerate(picked, 1):
        out += [
            f"## {i}. {c.case_id}: {c.label} ({c.scenario}, {c.difficulty})",
            "",
            f"Money at risk if wrongly approved: {fmt_money(c.amount_at_risk_pence)}",
            "",
            f"Rule that decides it: {RULES[c.scenario][0]}",
            "",
            *([f"**Possible disagreement:** {RULES[c.scenario][1]}", ""] if RULES[c.scenario][1] else []),
            "```",
            render_case(c),
            "```",
            "",
            "Your notes:",
            "",
        ]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(out))
    print(f"Wrote {len(picked)} cases to {args.out}")

    blind = args.out.with_name("review_blind.md")
    blind.write_text(blind_version(picked))
    print(f"Wrote the same {len(picked)} cases, without answers, to {blind}")


BLIND_INSTRUCTIONS = """\
# Invoice review task

You are reviewing supplier invoices for an accounts payable team, using the policy below.
Work only from this file. Do not open or search for any other files.

For each numbered case, decide which single outcome the policy requires. Then say whether
any other outcome is also defensible under the policy wording, and note anything about the
documents that looks unrealistic or that gives the answer away too easily.

Reply with one markdown table, one row per case, in this exact format:

| # | Outcome | Other defensible outcome (or none) | Why / notes |
|---|---|---|---|
| 1 | APPROVE | none | ... |

Use only these outcomes: APPROVE, SUPPLIER_MISMATCH, DUPLICATE, QUANTITY_VARIANCE,
PRICE_VARIANCE, TAX_ERROR, UNAPPLIED_CREDIT.
"""


def blind_version(picked) -> str:
    """The same cases with no label, scenario, rule or money-at-risk: only what a clerk sees."""
    out = [BLIND_INSTRUCTIONS, "## Policy", "", "```", POLICY_TEXT, "```", ""]
    for i, c in enumerate(picked, 1):
        out += [f"## Case {i}", "", "```", render_case(c), "```", ""]
    return "\n".join(out)


if __name__ == "__main__":
    main()
