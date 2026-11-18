"""Checks on the Claude runner that need no API calls."""

import pytest

from the_tell.generate import generate_cases
from the_tell.prompt import SYSTEM_PROMPT
from the_tell.run_claude import MODEL, SAMPLES, build_results, cost, custom_id, load_key, request_params


def test_key_comes_only_from_the_env_file(tmp_path, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-from-the-shell")
    with pytest.raises(SystemExit):
        load_key(tmp_path / ".env")  # no file: refuse, even though the shell has a key
    (tmp_path / ".env").write_text("OTHER=1\nANTHROPIC_API_KEY=sk-ant-test\n")
    assert load_key(tmp_path / ".env") == "sk-ant-test"


def test_request_matches_the_qwen_run_and_sends_no_sampling_settings():
    c = generate_cases(1, seed=7)[0]
    for thinking in ["off", "on"]:
        p = request_params(c, thinking)
        assert p["model"] == MODEL == "claude-haiku-5-5"
        assert p["system"][0]["text"] == SYSTEM_PROMPT
        assert not {"temperature", "top_p", "top_k"} & p.keys()  # Haiku 5.5 rejects them
    assert request_params(c, "off")["thinking"] == {"type": "disabled"}
    assert request_params(c, "on")["output_config"] == {"effort": "low"}


def test_cost_uses_the_cached_price_and_the_batch_discount():
    usage = {"input": 1_000_000, "output": 1_000_000, "cache_read": 1_000_000, "cache_write": 0}
    assert cost(usage, batch=False) == pytest.approx(0.61)
    assert cost(usage, batch=True) == pytest.approx(0.305)


def test_first_sample_is_the_answer_and_the_rest_measure_variation():
    c = generate_cases(1, seed=7)[0]
    replies = ["OUTCOME: APPROVE\nCONFIDENCE: 95"] + ["OUTCOME: DUPLICATE\nCONFIDENCE: 80"] * (SAMPLES - 1)
    calls = {custom_id(c.case_id, s): {"raw": raw, "stop_reason": "end_turn"} for s, raw in enumerate(replies)}
    [r] = build_results([c], calls)
    assert r["predicted"] == "APPROVE" and r["confidence"] == 95
    assert r["sample_answers"].count("DUPLICATE") == SAMPLES - 1


def test_invoices_missing_a_sample_are_left_out():
    c = generate_cases(1, seed=7)[0]
    calls = {custom_id(c.case_id, 0): {"raw": "OUTCOME: APPROVE\nCONFIDENCE: 90", "stop_reason": "end_turn"}}
    assert build_results([c], calls) == []
