"""Safety tests: every high-risk intent escalates (no silent auto-handle), and every decision writes
an audit entry. Educational demo — synthetic data only."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(ROOT, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "mock-llm"))
sys.path.insert(0, ROOT)

import mock_llm  # noqa: E402
from src.agent import handle, route, HIGH_RISK  # noqa: E402
from src.harness import Tracer  # noqa: E402


def _provider():
    return mock_llm.MockProvider(os.path.join(ROOT, "fixtures"))


def _golden():
    with open(os.path.join(ROOT, "eval", "golden.json"), encoding="utf-8") as fh:
        return json.load(fh)


def _run():
    provider, audit = _provider(), []
    tracer = Tracer("t", {"name": "healthcare-intake", "capability_tier": "L1"})
    entries = [handle(g["id"], g["message"], provider, tracer, audit) for g in _golden()]
    return entries, audit, tracer


def test_route_escalates_high_risk():
    assert route("emergency") == ("human-review", True)
    assert route("medication") == ("human-review", True)
    assert route("booking")[1] is False


def test_every_high_risk_intent_escalates():
    entries, _, _ = _run()
    high_risk = [e for e in entries if e["intent"] in HIGH_RISK]
    assert high_risk, "golden set must include high-risk intents"
    for e in high_risk:
        assert e["escalated"], f"high-risk intent {e['intent']} ({e['message_id']}) was NOT escalated"


def test_no_high_risk_is_silently_auto_handled():
    entries, _, _ = _run()
    auto_handled_high_risk = [e for e in entries if e["high_risk"] and not e["escalated"]]
    assert not auto_handled_high_risk, f"high-risk auto-handled (must escalate): {auto_handled_high_risk}"


def test_audit_entry_per_decision():
    entries, audit, _ = _run()
    assert len(audit) == len(entries), "every decision must write exactly one audit entry"
    for e in audit:
        assert {"message_id", "intent", "route", "escalated", "high_risk"} <= set(e)


def test_fail_safe_unknown_and_unparseable_escalate():
    # An unknown intent (m8) and an unparseable model response (m9) must fail SAFE — escalate, and be
    # recorded honestly as unrecognized (never relabelled to a real intent).
    entries, _, _ = _run()
    by_id = {e["message_id"]: e for e in entries}
    for mid in ("m8", "m9"):
        assert by_id[mid]["escalated"], f"{mid} fail-safe case must escalate"
        assert by_id[mid]["recognized"] is False, f"{mid} must be recorded as unrecognized"
        assert by_id[mid]["intent"] not in ("emergency", "medication"), (
            f"{mid} must not be relabelled to a real high-risk intent"
        )


def test_classification_matches_golden_expectations():
    entries, _, _ = _run()
    by_id = {e["message_id"]: e for e in entries}
    for g in _golden():
        assert by_id[g["id"]]["escalated"] == g["expectedEscalated"], (
            f"{g['id']}: escalation mismatch"
        )
