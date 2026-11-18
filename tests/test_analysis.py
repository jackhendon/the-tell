import numpy as np

from the_tell.analysis import answer_given_scores, bootstrap, cutoff_at_risk, coverage_at_risk, within_type_auroc, is_wrong, output_signals, risk_coverage, supplier_folds


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


def test_each_supplier_sits_in_exactly_one_fold():
    rs = [_result("APPROVE", "APPROVE", supplier=f"SUP-{i % 40:03d}") for i in range(400)]
    folds = supplier_folds(rs, k=5)
    for s in {r["supplier_id"] for r in rs}:
        assert len({f for r, f in zip(rs, folds) if r["supplier_id"] == s}) == 1
    assert sorted(set(folds)) == [0, 1, 2, 3, 4]


def test_bootstrap_ranges_bracket_a_perfect_and_a_useless_signal():
    rng = np.random.default_rng(1)
    y = rng.random(800) < 0.2
    groups = np.array([f"S{i % 40}" for i in range(800)])
    scores = {"probe": y + rng.random(800) * 0.1, "noise": rng.random(800)}
    ci = bootstrap(scores, y, np.ones(800, bool), groups)
    assert ci["probe.auroc"][0] > 0.99
    assert ci["noise.auroc"][0] < 0.5 < ci["noise.auroc"][1]
    assert ci["probe_minus.noise"][0] > 0.3


def test_more_certain_answers_get_lower_doubt():
    sure, unsure = _result("APPROVE", "APPROVE", top_logprob=-1e-7), _result("APPROVE", "APPROVE", top_logprob=-0.3)
    doubt = output_signals([sure, unsure])["answer_prob"]
    assert doubt[0] < doubt[1]


def test_knowing_the_case_type_scores_chance_within_type():
    """A score that only knows each invoice's type cannot separate right from wrong inside a type."""
    scenarios = np.array(["a"] * 10 + ["b"] * 10)
    y = np.array([True] * 4 + [False] * 6 + [True] * 3 + [False] * 7)
    type_rate = np.where(scenarios == "a", 0.4, 0.3)
    assert within_type_auroc(type_rate, y, np.ones(20, bool), scenarios)["auroc"] == 0.5
    assert within_type_auroc(y.astype(float), y, np.ones(20, bool), scenarios)["auroc"] == 1.0


def test_answer_given_learns_only_from_fit_invoices():
    rs = [_result("APPROVE", "PRICE_VARIANCE"), _result("PRICE_VARIANCE", "PRICE_VARIANCE"), _result("APPROVE", "APPROVE"), _result("TAX_ERROR", "APPROVE")]
    y = is_wrong(rs, "label")
    fit = np.array([True, True, True, False])  # the last invoice is a test invoice
    s = answer_given_scores(rs, y, fit)
    assert list(s) == [0.5, 0.5, 0.0, 0.0]  # "APPROVE" was never wrong among the fit invoices


def test_cutoff_is_the_highest_score_that_keeps_errors_in_bounds():
    score = np.arange(10.0)
    wrong = np.array([False] * 8 + [True, True])
    assert cutoff_at_risk(score, wrong, 0.0) == 7.0
    assert cutoff_at_risk(score, wrong, 0.2) == 9.0
    assert cutoff_at_risk(score, np.ones(10, bool), 0.02) == -np.inf  # nothing can be automated
