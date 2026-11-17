import numpy as np

from the_tell.analysis import coverage_at_risk, is_wrong, output_signals, risk_coverage, supplier_split


def _result(label, predicted, supplier="SUP-001", confidence=100, top_logprob=-1e-6):
    others = {l: -20.0 for l in ["APPROVE", "PRICE_VARIANCE", "TAX_ERROR"]}
    if predicted:
        others[predicted] = top_logprob
    return {"label": label, "predicted": predicted, "supplier_id": supplier, "confidence": confidence, "outcome_logprobs": others}


def test_risk_coverage_ranks_least_doubtful_first():
    score = np.array([0.1, 0.2, 0.9, 0.8])
    wrong = np.array([False, False, True, False])
    cov, risk = risk_coverage(score, wrong)
    assert list(cov) == [0.25, 0.5, 0.75, 1.0]
    assert list(risk) == [0.0, 0.0, 0.0, 0.25]


def test_tied_scores_cannot_be_split():
    """A signal that gives every invoice the same score can only automate all or nothing."""
    cov, risk = risk_coverage(np.full(4, 100.0), np.array([True, False, False, False]))
    assert list(cov) == [1.0] and list(risk) == [0.25]
    assert coverage_at_risk(np.full(4, 100.0), np.array([True, False, False, False]), 0.02) == 0.0


def test_coverage_at_risk():
    score = np.arange(10.0)
    wrong = np.array([False] * 8 + [True, True])
    assert coverage_at_risk(score, wrong, 0.0) == 0.8
    assert coverage_at_risk(score, wrong, 0.2) == 1.0


def test_two_levels_of_wrong():
    rs = [
        _result("PRICE_VARIANCE", "TAX_ERROR"),  # wrong reason, but still held
        _result("PRICE_VARIANCE", "APPROVE"),  # approved a bad invoice
        _result("APPROVE", "APPROVE"),
        _result("APPROVE", None),  # unreadable answer
    ]
    assert list(is_wrong(rs, "label")) == [True, True, False, True]
    assert list(is_wrong(rs, "hold")) == [False, True, False, True]


def test_supplier_split_keeps_each_supplier_in_one_group():
    rs = [_result("APPROVE", "APPROVE", supplier=f"SUP-{i % 40:03d}") for i in range(400)]
    split = supplier_split(rs)
    for s in {r["supplier_id"] for r in rs}:
        assert len({g for r, g in zip(rs, split) if r["supplier_id"] == s}) == 1
    assert set(split) == {"train", "val", "test"}


def test_more_certain_answers_get_lower_doubt():
    sure, unsure = _result("APPROVE", "APPROVE", top_logprob=-1e-7), _result("APPROVE", "APPROVE", top_logprob=-0.3)
    doubt = output_signals([sure, unsure])["answer_prob"]
    assert doubt[0] < doubt[1]
