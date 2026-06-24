"""Record step (OFF in CI). Authors the canned mock-provider fixtures for example 04 from the golden
set, so the run is offline + deterministic. Re-run only when a prompt or the golden inputs change:

    .venv/bin/python record_fixtures.py

There is no real-provider call here — the canned worker claims, themes, and synthesis ARE the golden
labels. That is what makes the run deterministic and the eval a test of the orchestration + grounding
logic, not the model. The fixtures are keyed by request hash, so the prompt builders in src/agents.py
must produce byte-identical requests at record-time and run-time.
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

FIXTURES = os.path.join(HERE, "fixtures")


def _resp(content_obj, in_tok, out_tok):
    return {
        "content": json.dumps(content_obj, sort_keys=True, separators=(",", ":")),
        "stop_reason": "end_turn",
        "usage": {"input_tokens": in_tok, "output_tokens": out_tok},
    }


# Two golden claims per source — 8 claims total, all grounded by construction (each cites its source).
GOLDEN_CLAIMS = {
    "src-obs": [
        "Emitting one trace event per agent step lets teams reconstruct any run end to end.",
        "Per-step tracing is the biggest lever on mean-time-to-diagnose for agent incidents.",
    ],
    "src-eval": [
        "A regression gate that blocks releases below an eval pass-rate threshold catches prompt drift.",
        "Treating the golden set as a unit test for the agent surfaces defects before they ship.",
    ],
    "src-cost": [
        "Attributing token usage per agent role makes runaway orchestrator loops visible in the bill.",
        "A per-role token budget is the cheapest cost guardrail and the first to pay off.",
    ],
    "src-trust": [
        "A groundedness check rejects any synthesized claim that lacks a source reference.",
        "Requiring a citation per claim stops the agent from asserting facts it cannot cite.",
    ],
}

# One synthesized claim per theme, each citing the source ids it draws on (kept in corpus → grounded).
GOLDEN_THEMES_ORDER = [
    ("Observability", "src-obs"),
    ("Evaluation", "src-eval"),
    ("Cost", "src-cost"),
    ("Trust", "src-trust"),
]


def main():
    golden = json.load(open(os.path.join(HERE, "eval", "golden.json"), encoding="utf-8"))
    sources = golden["sources"]

    n = 0
    # 1) Worker fixtures: one per source. The response is the golden claim set for that source.
    claims = []
    for source in sources:
        req = agents.worker_request(source)
        claim_objs = [{"text": t, "source": source["id"]} for t in GOLDEN_CLAIMS[source["id"]]]
        mock_llm.record(req, _resp({"claims": claim_objs}, 90, 40), FIXTURES)
        n += 1
        for c in claim_objs:
            claims.append({"text": c["text"], "source": source["id"], "worker": source["worker"]})

    # 2) Theme-grouping fixture: groups the flat claim list (built from the worker outputs above) into
    #    one theme per source, covering each claim exactly once.
    by_source_indexes = {}
    for i, c in enumerate(claims):
        by_source_indexes.setdefault(c["source"], []).append(i)
    themes = [{"name": name, "claim_indexes": by_source_indexes[sid]} for name, sid in GOLDEN_THEMES_ORDER]
    mock_llm.record(agents.group_request(claims), _resp({"themes": themes}, 160, 60), FIXTURES)
    n += 1

    # 3) Synthesis fixture: carry every grounded claim through to the answer (8 total), each tagged
    #    with its theme and citing its source id — so the groundedness eval runs over all 8 claims.
    synth_claims = []
    for name, sid in GOLDEN_THEMES_ORDER:
        for idx in by_source_indexes[sid]:
            synth_claims.append({"text": f"{name}: " + claims[idx]["text"], "sources": [sid]})
    answer = (
        "Reliable production agents rest on four load-bearing practices: per-step observability, "
        "evaluation gates, per-role cost attribution, and a groundedness check on every claim."
    )
    mock_llm.record(
        agents.synth_request(themes, claims),
        _resp({"answer": answer, "claims": synth_claims}, 220, 90),
        FIXTURES,
    )
    n += 1

    print(f"recorded {n} fixtures into {os.path.relpath(FIXTURES, HERE)}/")


if __name__ == "__main__":
    main()
