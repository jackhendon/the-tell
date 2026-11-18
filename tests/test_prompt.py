import pytest

from the_tell import oracle
from the_tell.domain import Label
from the_tell.facts import compute, render_facts
from the_tell.generate import generate_cases
from the_tell.prompt import build_messages, parse_answer, user_message


@pytest.fixture(scope="module")
def cases():
    return generate_cases(1500, seed=3)


def test_checks_state_facts_not_verdicts(cases):
    """The checks must never name an outcome or apply a rule, or the model has nothing left
    to judge. Words like 'tolerance' or 'should' would mean the code applied the policy."""
    banned = [*Label, "tolerance", "should", "allowed", "acceptable", "correct rate"]
    for c in cases:
        text = render_facts(compute(c))
        for word in banned:
            assert word not in text, (c.case_id, word)


def test_user_message_never_contains_the_answer(cases):
    for c in cases:
        msg = user_message(c)
        assert c.scenario not in msg
        for label in Label:
            assert label not in msg, (c.case_id, label)


def test_quantity_facts_agree_with_the_oracle(cases):
    """Where the oracle finds over-invoicing, the checks show total invoiced above received."""
    for c in cases:
        over = any(l.invoiced_total > l.received for l in compute(c).lines)
        assert over == oracle.quantity_variance(c), c.case_id


def test_duplicate_facts_agree_with_the_oracle(cases):
    for c in cases:
        flagged = any(identical for _, identical in compute(c).earlier_same_po)
        assert flagged == oracle.duplicate(c), c.case_id


def test_system_prompt_is_identical_for_every_case(cases):
    """Identical system prompts can be cached by Claude, and keep the comparison fair."""
    assert len({build_messages(c)[0]["content"] for c in cases[:200]}) == 1


@pytest.mark.parametrize(
    "reply, label, confidence",
    [
        ("OUTCOME: PRICE_VARIANCE\nCONFIDENCE: 85", Label.PRICE_VARIANCE, 85),
        ("  OUTCOME:APPROVE\nCONFIDENCE:100", Label.APPROVE, 100),
        ("OUTCOME: PRICE_PROBLEM\nCONFIDENCE: 60", None, 60),  # not a real outcome
        ("OUTCOME: TAX_ERROR\nCONFIDENCE: 150", Label.TAX_ERROR, None),  # out of range
        ("I think this should be approved.", None, None),
    ],
)
def test_parse_answer(reply, label, confidence):
    a = parse_answer(reply)
    assert a.label == label
    assert a.confidence == confidence


def test_reasoning_written_before_the_answer_is_skipped():
    reply = "Checking each rule.\nPRICE: +1.6%, inside tolerance.\n\nOUTCOME: APPROVE\nCONFIDENCE: 90"
    a = parse_answer(reply)
    assert a.label.value == "APPROVE" and a.confidence == 90
