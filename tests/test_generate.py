from collections import Counter

import pytest

from the_tell import oracle
from the_tell.catalogue import PRODUCTS, ZERO_RATED_CATEGORIES
from the_tell.domain import Label, lines_net_pence, lines_vat_pence
from the_tell.generate import SCENARIOS, generate_cases, read_jsonl, write_jsonl


@pytest.fixture(scope="module")
def cases():
    return generate_cases(3000, seed=1)


def test_every_label_agrees_with_the_oracle(cases):
    # generate_cases already raises on disagreement; this makes the guarantee explicit.
    for c in cases:
        assert oracle.correct_label(c) == c.label, c.case_id


def test_each_case_has_exactly_one_problem(cases):
    """Labels are unambiguous: approve cases have no issue, others have exactly one.

    The one allowed overlap: a duplicate also over-invoices quantities, and the policy's
    precedence order resolves that in favour of DUPLICATE.
    """
    for c in cases:
        found = oracle.issues(c)
        if c.label == Label.APPROVE:
            assert found == [], (c.case_id, c.scenario, found)
        elif c.label == Label.DUPLICATE:
            assert set(found) <= {Label.DUPLICATE, Label.QUANTITY_VARIANCE}, (c.case_id, found)
        else:
            assert found == [c.label], (c.case_id, c.scenario, found)


def test_generation_is_reproducible():
    a = generate_cases(200, seed=42)
    b = generate_cases(200, seed=42)
    assert [x.model_dump() for x in a] == [x.model_dump() for x in b]


def test_label_mix_matches_plan(cases):
    counts = Counter(c.label for c in cases)
    assert counts[Label.APPROVE] == 900
    for label in Label:
        if label != Label.APPROVE:
            assert counts[label] == 350


def test_every_scenario_appears(cases):
    seen = {(c.label, c.scenario) for c in cases}
    for s in SCENARIOS:
        assert (s.label, s.name) in seen, s.name


def test_money_at_risk_only_on_problem_invoices(cases):
    for c in cases:
        if c.label == Label.APPROVE:
            assert c.amount_at_risk_pence == 0
        else:
            assert c.amount_at_risk_pence > 0, (c.case_id, c.scenario)


def test_invoice_totals_add_up(cases):
    for c in cases:
        inv = c.invoice
        if c.scenario == "vat_sum_wrong":
            continue  # deliberately wrong
        credits = sum(a.amount_pence for a in inv.credits_applied)
        assert inv.vat_total_pence == lines_vat_pence(inv.lines)
        assert inv.total_due_pence == lines_net_pence(inv.lines) + inv.vat_total_pence - credits
        assert inv.total_due_pence > 0


def test_catalogue_vat_matches_policy_table():
    for p in PRODUCTS:
        if p.category in ZERO_RATED_CATEGORIES:
            assert p.vat_rate_pct == 0, p.sku
        else:
            assert p.vat_rate_pct == 20, p.sku


def test_jsonl_round_trip(tmp_path, cases):
    path = tmp_path / "cases.jsonl"
    write_jsonl(cases[:50], path)
    assert [c.model_dump() for c in read_jsonl(path)] == [c.model_dump() for c in cases[:50]]


def test_invoice_numbers_rise_with_dates(cases):
    """Suppliers number invoices in order. If numbering were random, 'a nearby number'
    would be a clue only duplicates carry, and the model could learn that instead of
    the rule. Resent invoices keep their original number, so they are exempt."""
    def num(n: str) -> int:
        return int(n.split("-")[-1])

    for c in cases:
        if c.scenario in ("same_number", "reformatted_number"):
            continue
        docs = sorted([(p.date, num(p.invoice_number)) for p in c.prior_invoices] + [(c.invoice.date, num(c.invoice.invoice_number))])
        numbers = [n for _, n in docs]
        assert numbers == sorted(numbers), (c.case_id, c.scenario, docs)


def test_agreed_price_changes_postdate_the_po(cases):
    """A price change dated before the PO would make 'should the PO already include it?'
    a fair question, and the label would stop being forced by the policy."""
    for c in cases:
        for a in c.purchase_order.price_agreements:
            assert a.effective > c.purchase_order.date, (c.case_id, c.scenario)
