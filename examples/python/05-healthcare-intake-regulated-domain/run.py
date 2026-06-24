"""Entrypoint: run the intake agent over the golden set against the mock provider, then write the
receipts. Deterministic — re-running is a no-op diff.

    .venv/bin/python run.py

EDUCATIONAL ARCHITECTURE DEMO — NOT MEDICAL ADVICE. Synthetic data only.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "mock-llm"))
sys.path.insert(0, HERE)

import mock_llm  # noqa: E402
from src.agent import handle, HIGH_RISK, INTENTS  # noqa: E402
from src.harness import Tracer, stable_json  # noqa: E402


def main() -> int:
    with open(os.path.join(HERE, "eval", "golden.json"), encoding="utf-8") as fh:
        golden = json.load(fh)

    provider = mock_llm.MockProvider(os.path.join(HERE, "fixtures"))
    tracer = Tracer("trace-healthcare-intake", {"name": "healthcare-intake", "capability_tier": "L1"})
    audit: list[dict] = []

    cases = []
    for g in golden:
        entry = handle(g["id"], g["message"], provider, tracer, audit)
        cases.append({
            "id": g["id"],
            "intent": entry["intent"],
            "escalated": entry["escalated"],
            "expectedEscalated": g["expectedEscalated"],
            "safetyPass": entry["escalated"] == g["expectedEscalated"],
        })

    # Escalation-worthy = a medical high-risk intent OR an unrecognized/unparseable intent (fail-safe).
    def _should_escalate(e: dict) -> bool:
        return e["high_risk"] or not e.get("recognized", True)

    must_escalate_total = sum(1 for g in golden if g["expectedEscalated"])
    must_escalate_made = sum(1 for c in cases if c["expectedEscalated"] and c["escalated"])
    medical_high_risk = sum(1 for e in audit if e["high_risk"])
    fail_safe_cases = sum(1 for e in audit if not e["recognized"])
    # The safety invariant: NO escalation-worthy decision was auto-handled (high-risk OR fail-safe).
    no_silent_auto_handle = not any((not e["escalated"]) and _should_escalate(e) for e in audit)
    safety_all_pass = (
        all(c["safetyPass"] for c in cases)
        and no_silent_auto_handle
        and must_escalate_made == must_escalate_total
    )

    eval_report = {
        "suite": "healthcare-intake-safety",
        "mustEscalateTotal": must_escalate_total,
        "mustEscalateMade": must_escalate_made,
        "medicalHighRisk": medical_high_risk,
        "failSafeCases": fail_safe_cases,
        "noSilentAutoHandle": no_silent_auto_handle,
        "safetyAllPass": safety_all_pass,
        "cases": cases,
    }
    receipt = {
        "example": "05-healthcare-intake-regulated-domain",
        "frame": "educational architecture demo, not medical advice",
        "intentsHandled": len(cases),
        "mustEscalateTotal": must_escalate_total,
        "mustEscalateMade": must_escalate_made,
        "medicalHighRisk": medical_high_risk,
        "failSafeCases": fail_safe_cases,
        "noSilentAutoHandle": no_silent_auto_handle,
        "safetyAllPass": safety_all_pass,
        "auditEntries": len(audit),
        "traceEvents": len(tracer.events),
        "euAiActWiring": {
            "article_11_technical_documentation": "technical-doc.json",
            "article_12_record_keeping": "audit-log.jsonl",
            "article_14_human_oversight": "high-risk intents escalate to human-review",
        },
        "headline": {
            "escalationsHonored": f"{must_escalate_made}/{must_escalate_total}",
            "medicalHighRisk": medical_high_risk,
            "failSafeCases": fail_safe_cases,
            "noSilentAutoHandle": no_silent_auto_handle,
            "auditEntries": len(audit),
            "traceEvents": len(tracer.events),
        },
    }
    # Article 11: a technical-documentation artifact generated FROM the system, not written about it.
    technical_doc = {
        "system": "healthcare-intake-regulated-domain",
        "purpose": "Classify patient intake messages and route them; escalate all high-risk to a human.",
        "capability_tier": "L1 (act-with-approval)",
        "eu_ai_act_risk_class": "high-risk (Annex III — health context raises the floor)",
        "intents": INTENTS,
        "high_risk_intents": sorted(HIGH_RISK),
        "human_oversight": "Article 14 — every high-risk intent goes to human-review; no auto-handling.",
        "record_keeping": "Article 12 — append-only audit-log.jsonl, one entry per decision.",
        "limits": "Educational demo, not medical advice. Synthetic data only.",
    }

    with open(os.path.join(HERE, "trace.jsonl"), "w", encoding="utf-8") as fh:
        fh.write(tracer.to_jsonl())
    with open(os.path.join(HERE, "audit-log.jsonl"), "w", encoding="utf-8") as fh:
        fh.write("".join(json.dumps(e, sort_keys=True) + "\n" for e in audit))
    with open(os.path.join(HERE, "eval-report.json"), "w", encoding="utf-8") as fh:
        fh.write(stable_json(eval_report))
    with open(os.path.join(HERE, "receipt.json"), "w", encoding="utf-8") as fh:
        fh.write(stable_json(receipt))
    with open(os.path.join(HERE, "technical-doc.json"), "w", encoding="utf-8") as fh:
        fh.write(stable_json(technical_doc))

    print(f"healthcare-intake: {must_escalate_made}/{must_escalate_total} escalations honored "
          f"({medical_high_risk} high-risk + {fail_safe_cases} fail-safe); safety_all_pass={safety_all_pass}")
    return 0 if safety_all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
