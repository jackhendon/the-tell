"""The prompt every model receives, and the code that reads its answer.

The same messages go to the local open model and to Claude, so any difference in their
results comes from the model, not the wording.

The model answers in two fixed lines:
    OUTCOME: PRICE_VARIANCE
    CONFIDENCE: 85
The first gives the decision, and the probability the model puts on each possible
outcome at that point (signal 3). The second is its stated confidence (signal 1).

Run:  uv run python -m the_tell.prompt        (writes data/prompt_examples.md)
"""

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

from the_tell.domain import Case, Label
from the_tell.facts import compute, render_facts
from the_tell.policy import BUYER, POLICY_TEXT
from the_tell.render import render_case

OUTCOME_PREFIX = "OUTCOME: "  # the model's answer starts here; step 3 reads probabilities at this point

SYSTEM_PROMPT = f"""\
You review supplier invoices for the accounts payable team at {BUYER}.
Apply the policy below exactly as written. The automated checks are correct arithmetic,
but they do not apply the policy: that is your job.

{POLICY_TEXT}
Reply with exactly two lines and nothing else:
{OUTCOME_PREFIX}<one of {", ".join(Label)}>
CONFIDENCE: <a whole number from 0 to 100: the probability that your outcome is correct>
"""


def user_message(c: Case) -> str:
    return f"{render_case(c)}\n\n{render_facts(compute(c))}\n\nDecide the outcome for this invoice."


def build_messages(c: Case) -> list[dict]:
    """Chat messages in the common role/content format. The system prompt is identical for
    every case, so with Claude it can be cached; only the user message changes."""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message(c)},
    ]


@dataclass
class Answer:
    label: Label | None  # None if the reply could not be read
    confidence: int | None
    raw: str


_OUTCOME = re.compile(r"OUTCOME:\s*([A-Z_]+)")
_CONFIDENCE = re.compile(r"CONFIDENCE:\s*(\d{1,3})")


def _last(pattern: re.Pattern, text: str) -> re.Match | None:
    matches = list(pattern.finditer(text))
    return matches[-1] if matches else None


def parse_answer(text: str) -> Answer:
    """Reads the reply. Anything unreadable becomes None and is counted as an error later,
    never silently guessed."""
    # The last match counts: a model that writes out its reasoning first may mention the
    # format along the way, but its final lines are its answer.
    m = _last(_OUTCOME, text)
    label = Label(m.group(1)) if m and m.group(1) in Label.__members__ else None
    m = _last(_CONFIDENCE, text)
    confidence = int(m.group(1)) if m and int(m.group(1)) <= 100 else None
    return Answer(label=label, confidence=confidence, raw=text)


def main() -> None:
    from the_tell.generate import read_jsonl

    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", type=Path, default=Path("data/generated/cases.jsonl"))
    ap.add_argument("--out", type=Path, default=Path("data/prompt_examples.md"))
    args = ap.parse_args()

    cases = read_jsonl(args.cases)
    # Three illustrative cases: a tricky approve, a price problem, a credit problem.
    wanted = ["agreed_uplift", "just_over", "refund_separately"]
    examples = [next(c for c in cases if c.scenario == s) for s in wanted]

    out = [
        "# What the model receives",
        "",
        "Every case gets the same system prompt, followed by one user message with the",
        "documents and the automated checks. Three examples follow, with the correct answer",
        "shown above each (the model never sees it).",
        "",
        "## System prompt (identical for every case)",
        "",
        "```",
        SYSTEM_PROMPT,
        "```",
    ]
    for c in examples:
        out += ["", f"## {c.case_id}: correct answer {c.label} ({c.scenario})", "", "```", user_message(c), "```"]
    args.out.write_text("\n".join(out) + "\n")

    # Rough size, at about 4 characters per token. Step 3 measures real token counts.
    sizes = sorted(len(SYSTEM_PROMPT) + len(user_message(c)) for c in cases)
    median, largest = sizes[len(sizes) // 2], sizes[-1]
    print(f"Wrote {len(examples)} examples to {args.out}")
    print(f"Prompt size over {len(cases)} cases: median ~{median // 4} tokens, largest ~{largest // 4} tokens")


if __name__ == "__main__":
    main()
