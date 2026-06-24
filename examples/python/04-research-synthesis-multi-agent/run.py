"""Entrypoint: run the research-synthesis multi-agent over the golden corpus against the mock provider,
then write the receipts: trace.jsonl, eval-report.json, receipt.json. Deterministic — re-running is a
no-op diff (canned fixtures + a synthetic clock; no datetime.now(), no random).

    .venv/bin/python run.py
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "mock-llm"))
sys.path.insert(0, HERE)

import mock_llm  # noqa: E402
from src import agents  # noqa: E402
from src.harness import Tracer, stable_json  # noqa: E402


def main() -> int:
    golden = json.load(open(os.path.join(HERE, "eval", "golden.json"), encoding="utf-8"))
    sources = golden["sources"]
    valid_source_ids = [s["id"] for s in sources]
    gate = golden["rubric"]["gate"]

    provider = mock_llm.MockProvider(os.path.join(HERE, "fixtures"))
    tracer = Tracer("trace-research-synthesis", {"name": "research-synthesis", "capability_tier": "L2"})
    ledger = agents.TokenLedger()

    # Orchestrator-worker with explicit artifact handoff:
    claims = agents.run_workers(sources, provider, tracer, ledger)           # workers -> claim artifacts
    themes = agents.group_themes(claims, provider, tracer, ledger)           # orchestrator -> themes
    synthesized = agents.synthesize(themes, claims, provider, tracer, ledger)  # orchestrator -> answer
    per_claim, grounded, total = agents.evaluate_groundedness(               # evaluator -> verdict
        synthesized, valid_source_ids, tracer
    )

    groundedness = round(grounded / total, 4) if total else 0.0
    orchestrator_tokens = ledger.by_role[agents.ORCHESTRATOR]
    worker_tokens = ledger.by_role[agents.WORKER]
    total_tokens = ledger.total

    eval_report = {
        "suite": "research-synthesis-groundedness",
        "question": golden["question"],
        "gate": gate,
        "groundednessScore": groundedness,
        "claimsGrounded": grounded,
        "claimsTotal": total,
        "gatePassed": groundedness >= gate,
        "perClaim": per_claim,
        "themes": [t["name"] for t in themes],
        "tokenSplit": {
            "orchestrator": orchestrator_tokens,
            "worker": worker_tokens,
            "total": total_tokens,
        },
    }

    receipt = {
        "example": "04-research-synthesis-multi-agent",
        "pattern": "orchestrator-worker with explicit artifact handoff",
        "groundednessScore": groundedness,
        "claimsGrounded": grounded,
        "claimsTotal": total,
        "gate": gate,
        "gatePassed": groundedness >= gate,
        "orchestratorTokens": orchestrator_tokens,
        "workerTokens": worker_tokens,
        "totalTokens": total_tokens,
        "traceEvents": len(tracer.events),
        # headline: every value here MUST appear verbatim in README.md (the prose-vs-receipt gate).
        "headline": {
            "groundednessScore": f"{round(groundedness * 100)}%",
            "claimsGrounded": f"{grounded}/{total}",
            "orchestratorTokens": orchestrator_tokens,
            "workerTokens": worker_tokens,
            "traceEvents": len(tracer.events),
        },
    }

    with open(os.path.join(HERE, "trace.jsonl"), "w", encoding="utf-8") as fh:
        fh.write(tracer.to_jsonl())
    with open(os.path.join(HERE, "eval-report.json"), "w", encoding="utf-8") as fh:
        fh.write(stable_json(eval_report))
    with open(os.path.join(HERE, "receipt.json"), "w", encoding="utf-8") as fh:
        fh.write(stable_json(receipt))

    print(
        f"research-synthesis: {grounded}/{total} claims grounded (score {groundedness}, gate {gate}); "
        f"tokens orchestrator={orchestrator_tokens} worker={worker_tokens} total={total_tokens}"
    )
    return 0 if receipt["gatePassed"] else 1


if __name__ == "__main__":
    sys.exit(main())
