"""Pytest suite for example 04 (research-synthesis multi-agent). Stdlib + mock provider only — runs
offline. Asserts: every synthesized claim is grounded (100%), the per-role token split sums to the
total, the orchestrator/worker roles are genuinely separate, and the run is byte-deterministic.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXAMPLE = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(EXAMPLE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "mock-llm"))
sys.path.insert(0, EXAMPLE)

import mock_llm  # noqa: E402
from src import agents  # noqa: E402
from src.harness import Tracer  # noqa: E402


def _golden():
    return json.load(open(os.path.join(EXAMPLE, "eval", "golden.json"), encoding="utf-8"))


def _provider():
    return mock_llm.MockProvider(os.path.join(EXAMPLE, "fixtures"))


def _tracer():
    return Tracer("test", {"name": "research-synthesis", "capability_tier": "L2"})


def _run_pipeline():
    golden = _golden()
    sources = golden["sources"]
    provider = _provider()
    tracer = _tracer()
    ledger = agents.TokenLedger()
    claims = agents.run_workers(sources, provider, tracer, ledger)
    themes = agents.group_themes(claims, provider, tracer, ledger)
    synthesized = agents.synthesize(themes, claims, provider, tracer, ledger)
    per_claim, grounded, total = agents.evaluate_groundedness(
        synthesized, [s["id"] for s in sources], tracer
    )
    return claims, themes, synthesized, per_claim, grounded, total, ledger, tracer


# ---- groundedness ---------------------------------------------------------------------------------


def test_every_synthesized_claim_is_grounded():
    _, _, _, per_claim, grounded, total, _, _ = _run_pipeline()
    assert total > 0
    assert grounded == total, "some synthesized claim lacks a valid source ref"
    assert grounded / total == 1.0  # 100% groundedness
    assert all(c["grounded"] for c in per_claim)
    assert all(c["sources"] for c in per_claim), "a synthesized claim cites no source"


def test_groundedness_matches_expected_claim_count():
    golden = _golden()
    _, _, synthesized, _, grounded, total, _, _ = _run_pipeline()
    assert total == golden["rubric"]["expected_claims"]
    assert grounded == golden["rubric"]["expected_claims"]


def test_evaluator_rejects_an_uncited_claim():
    # Feed the evaluator a fabricated claim with no sources — it must be flagged ungrounded.
    fake = {"answer": "x", "claims": [{"text": "uncited", "sources": []}]}
    per_claim, grounded, total = agents.evaluate_groundedness(fake, ["src-obs"], _tracer())
    assert grounded == 0 and total == 1
    assert per_claim[0]["grounded"] is False


def test_evaluator_rejects_a_claim_citing_an_unknown_source():
    fake = {"answer": "x", "claims": [{"text": "hallucinated", "sources": ["src-not-in-corpus"]}]}
    _, grounded, total = agents.evaluate_groundedness(fake, ["src-obs"], _tracer())
    assert grounded == 0 and total == 1


# ---- per-role token split -------------------------------------------------------------------------


def test_token_split_sums_to_total():
    *_, ledger, _ = _run_pipeline()
    split = ledger.by_role
    assert split[agents.ORCHESTRATOR] + split[agents.WORKER] == ledger.total
    assert ledger.total > 0
    assert split[agents.ORCHESTRATOR] > 0 and split[agents.WORKER] > 0


def test_workers_and_orchestrator_are_separate_roles():
    # Four workers, two orchestrator steps (group + synthesize) — distinct roles in the trace.
    _, _, _, _, _, _, _, tracer = _run_pipeline()
    roles = [e["attributes"].get("role") for e in tracer.events if "attributes" in e]
    assert roles.count(agents.WORKER) == 4
    assert roles.count(agents.ORCHESTRATOR) == 2


# ---- handoff + receipt agreement ------------------------------------------------------------------


def test_claims_handed_off_are_structured_and_grouped_once():
    claims, themes, _, _, _, total, _, _ = _run_pipeline()
    assert len(claims) == 8
    assert all(set(c) >= {"text", "source", "worker"} for c in claims)
    # Every claim index is covered exactly once across the themes (orchestrator artifact integrity).
    covered = [i for t in themes for i in t["claim_indexes"]]
    assert sorted(covered) == list(range(len(claims)))


def test_missing_fixture_raises_on_a_drifted_prompt():
    provider = _provider()
    drifted = agents.worker_request(
        {"id": "src-x", "title": "unseen", "snippet": "never recorded", "worker": "w"}
    )
    try:
        provider.complete(drifted)
        assert False, "expected MissingFixture on an unrecorded request"
    except mock_llm.MissingFixture:
        pass


def test_committed_receipt_is_100_percent_grounded_and_token_split_sums():
    receipt = json.load(open(os.path.join(EXAMPLE, "receipt.json"), encoding="utf-8"))
    assert receipt["groundednessScore"] == 1.0
    assert receipt["claimsGrounded"] == receipt["claimsTotal"]
    assert receipt["headline"]["groundednessScore"] == "100%"
    assert receipt["orchestratorTokens"] + receipt["workerTokens"] == receipt["totalTokens"]


def test_run_is_byte_deterministic():
    artifacts = ["trace.jsonl", "eval-report.json", "receipt.json"]
    before = {a: open(os.path.join(EXAMPLE, a), "rb").read() for a in artifacts}
    subprocess.run([sys.executable, "run.py"], cwd=EXAMPLE, check=True, capture_output=True)
    for a in artifacts:
        after = open(os.path.join(EXAMPLE, a), "rb").read()
        assert after == before[a], f"{a} changed on re-run (non-deterministic)"
