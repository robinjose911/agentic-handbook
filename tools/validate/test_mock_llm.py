"""Validator: the mock LLM provider (Python binding) is deterministic and refuses unrecorded input."""
import os
import sys

import pytest

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "mock-llm"))

import mock_llm  # noqa: E402

RECORDED = {
    "system": "You are a support triage assistant. Reply with one label.",
    "messages": [{"role": "user", "content": "My card was declined at checkout."}],
    "tools": [],
}


def test_recorded_fixture_returns_exact_completion():
    resp = mock_llm.MockProvider().complete(RECORDED)
    assert resp["content"] == "billing"
    assert resp["stop_reason"] == "end_turn"


def test_unrecorded_hash_raises():
    drifted = dict(RECORDED, system="a prompt that was never recorded")
    with pytest.raises(mock_llm.MissingFixture):
        mock_llm.MockProvider().complete(drifted)


def test_hash_is_stable_and_key_order_independent():
    h1 = mock_llm.hash_request(RECORDED)
    reordered = {"tools": [], "messages": RECORDED["messages"], "system": RECORDED["system"]}
    assert h1 == mock_llm.hash_request(reordered)
    # Determinism across calls.
    assert h1 == mock_llm.hash_request(dict(RECORDED))


def test_cross_language_hash_matches_typescript():
    # The fixture filename is the canonical hash; it must equal what the Python binding computes.
    expected = "f59c6512beb20f88ae1c4d5d3b06084f15378bdb89915dcf96d4b6f0c61f478e"
    assert mock_llm.hash_request(RECORDED) == expected
    assert os.path.exists(
        os.path.join(REPO, "tools", "mock-llm", "fixtures", f"{expected}.json")
    )


def test_two_completions_are_identical():
    p = mock_llm.MockProvider()
    assert p.complete(RECORDED) == p.complete(RECORDED)


def test_integer_valued_floats_normalize_for_cross_language_parity():
    # A whole-number float (1.0) must hash the same as the int 1, so Python and JS — where
    # JSON.stringify(1.0) is "1" — agree on the fixture filename.
    with_float = dict(RECORDED, tools=[{"name": "f", "schema": {"multipleOf": 1.0}}])
    with_int = dict(RECORDED, tools=[{"name": "f", "schema": {"multipleOf": 1}}])
    assert mock_llm.hash_request(with_float) == mock_llm.hash_request(with_int)


def test_out_of_range_numbers_are_rejected():
    # Non-finite or >= 2**53 numbers can't canonicalize identically across languages, so both bindings
    # reject them (loud + symmetric) instead of producing a silent cross-language hash split.
    for bad in (float("nan"), float("inf"), float("-inf"), 2 ** 53, 1e21):
        with pytest.raises(ValueError):
            mock_llm.hash_request(dict(RECORDED, tools=[{"n": bad}]))


def test_record_writes_canonical_bytes(tmp_path):
    # record() output is the canonical form: sorted keys, no spaces, integer-valued floats collapsed.
    req = {"system": "s", "messages": [], "tools": [{"b": 2, "a": 1.0}]}
    resp = {"content": "ok"}
    path = mock_llm.record(req, resp, str(tmp_path))
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    assert '"a":1' in text and '"a":1.0' not in text  # integer-valued float normalized
    assert ", " not in text and '": ' not in text  # no spaces (canonical separators)
