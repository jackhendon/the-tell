from the_tell.compare_claude import output_signals


def test_disagreement_counts_answers_that_differ_from_the_first():
    rs = [
        {"confidence": 95, "sample_answers": ["APPROVE"] * 5},
        {"confidence": 90, "sample_answers": ["APPROVE", "DUPLICATE", "APPROVE", "DUPLICATE", "TAX_ERROR"]},
        {"confidence": None, "sample_answers": ["APPROVE"] * 5},
    ]
    s = output_signals(rs)
    assert list(s["disagreement"]) == [0.0, 0.75, 0.0]
    assert list(s["stated"]) == [5, 10, 100]  # an unreadable confidence counts as full doubt
