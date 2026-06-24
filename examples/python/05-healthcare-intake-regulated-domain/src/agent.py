"""Healthcare-intake agent (regulated domain). Classifies an intake message into an intent with a
reason code, then routes it — high-risk intents ALWAYS escalate to human review (no silent
auto-handle). Every decision writes an immutable audit-log entry. This wires EU AI Act Article 12
(record-keeping) and Article 14 (human oversight) into the architecture, not as an afterthought.

EDUCATIONAL ARCHITECTURE DEMO — NOT MEDICAL ADVICE. Synthetic data only.
"""
from __future__ import annotations

import json
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "mock-llm"))
import mock_llm  # noqa: E402

INTENTS = ["booking", "reschedule", "medication", "emergency", "insurance", "admin"]
# High-risk intents must go to a human — clinical-safety decisions are never auto-handled.
HIGH_RISK = {"emergency", "medication"}

SYSTEM = (
    "You are a healthcare front-desk intake classifier. This is an educational demo, not medical "
    "advice. Read the patient message and reply with ONLY a JSON object "
    '{"intent": one of ["booking","reschedule","medication","emergency","insurance","admin"], '
    '"reason_code": a short SCREAMING_SNAKE_CASE code}. Never give medical advice.'
)


def classify_request(message: str) -> dict:
    return {"system": SYSTEM, "messages": [{"role": "user", "content": message}], "tools": []}


def route(intent: str) -> tuple[str, bool]:
    """Return (route, escalated). High-risk intents escalate to human review."""
    if intent in HIGH_RISK:
        return "human-review", True
    return f"queue:{intent}", False


def handle(message_id: str, message: str, provider, tracer, audit) -> dict:
    """Classify + route one intake message, emitting a trace event and an immutable audit entry."""
    resp = provider.complete(classify_request(message))
    try:
        data = json.loads(str(resp["content"]))
        intent = data.get("intent")
        reason_code = data.get("reason_code", "UNKNOWN")
    except (json.JSONDecodeError, TypeError):
        intent, reason_code = None, "UNPARSEABLE"
    recognized = intent in INTENTS
    if recognized:
        dest, escalated = route(intent)
    else:
        # Fail safe: an unrecognized / unparseable intent escalates to a human and is recorded
        # HONESTLY as what it was (None/unknown) — never relabelled to a real intent.
        intent = intent if isinstance(intent, str) and intent else "unknown"
        dest, escalated = "human-review", True

    tracer.emit("llm_call", "ok", {"message_id": message_id, "intent": intent})
    tracer.emit(
        "escalation" if escalated else "decision",
        "escalated" if escalated else "ok",
        {"message_id": message_id, "intent": intent, "reason_code": reason_code, "route": dest},
    )
    entry = {
        "message_id": message_id,
        "intent": intent,
        "reason_code": reason_code,
        "route": dest,
        "escalated": escalated,
        "high_risk": intent in HIGH_RISK,
        "recognized": recognized,
    }
    audit.append(entry)  # Article 12: immutable record-keeping (append-only).
    return entry
