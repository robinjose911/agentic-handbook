"""Research-synthesis multi-agent — orchestrator/worker with explicit artifact handoff.

Roles are separate and hand off STRUCTURED artifacts, never prose:

  question + mock search results
        |
        v   (orchestrator delegates one source per worker)
  [worker]  extract_claims(source)  -> ClaimSet   (one mock llm_call per worker)
        |
        v   (orchestrator collects ClaimSets)
  [orchestrator] group_into_themes(claims)  -> Themes      (one mock llm_call)
  [orchestrator] synthesize(themes, claims)  -> Answer w/ source refs (one mock llm_call)
        |
        v
  [evaluator] groundedness(answer) -> every synthesized claim cites a source id

Every LLM call is a recorded mock fixture, so the run is offline + deterministic. Token usage is
summed per role (orchestrator vs worker) for the receipt's per-role split.

The prompt builders below are the single source of truth for both the record step and the run — if
they drift, the request hash won't match the fixture and MissingFixture fires loudly.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List

# ---- roles ----------------------------------------------------------------------------------------
ORCHESTRATOR = "orchestrator"
WORKER = "worker"

# ---- prompt builders (shared by record_fixtures.py and run.py) ------------------------------------

WORKER_SYSTEM = (
    "You are a research worker. Read ONE search result and extract the load-bearing factual claims. "
    'Reply with ONLY a JSON object {"claims": [{"text": str, "source": <the source id you were given>}]}. '
    "Every claim MUST carry the source id of the result you were given. Do not invent sources."
)


def worker_request(source: Dict[str, Any]) -> Dict[str, Any]:
    """Build the claim-extraction request for one source (the worker's input artifact)."""
    user = json.dumps(
        {"source": source["id"], "title": source["title"], "snippet": source["snippet"]},
        sort_keys=True,
        separators=(",", ":"),
    )
    return {"system": WORKER_SYSTEM, "messages": [{"role": "user", "content": user}], "tools": []}


GROUP_SYSTEM = (
    "You are the research orchestrator. Group the worker-extracted claims into themes. "
    'Reply with ONLY a JSON object {"themes": [{"name": str, "claim_indexes": [int]}]}. '
    "Use a claim's index (its position in the input list). Cover every claim exactly once."
)


def group_request(claims: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build the theme-grouping request (orchestrator input artifact = the flat claim list)."""
    indexed = [{"index": i, "text": c["text"], "source": c["source"]} for i, c in enumerate(claims)]
    user = json.dumps({"claims": indexed}, sort_keys=True, separators=(",", ":"))
    return {"system": GROUP_SYSTEM, "messages": [{"role": "user", "content": user}], "tools": []}


SYNTH_SYSTEM = (
    "You are the research orchestrator writing the final synthesis. For each theme, write one "
    "synthesized claim and cite the source ids it draws on. "
    'Reply with ONLY a JSON object {"answer": str, "claims": [{"text": str, "sources": [str]}]}. '
    "Every synthesized claim MUST cite at least one source id. Never assert a claim you cannot cite."
)


def synth_request(themes: List[Dict[str, Any]], claims: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build the synthesis request (orchestrator input = themes + the grounded claim list)."""
    user = json.dumps(
        {
            "themes": themes,
            "claims": [{"text": c["text"], "source": c["source"]} for c in claims],
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return {"system": SYNTH_SYSTEM, "messages": [{"role": "user", "content": user}], "tools": []}


# ---- the run pipeline -----------------------------------------------------------------------------


class TokenLedger:
    """Sums recorded usage per role so the receipt can publish a per-role token split."""

    def __init__(self) -> None:
        self.by_role: Dict[str, int] = {ORCHESTRATOR: 0, WORKER: 0}

    def add(self, role: str, usage: Dict[str, int]) -> int:
        n = int(usage.get("input_tokens", 0)) + int(usage.get("output_tokens", 0))
        self.by_role[role] = self.by_role.get(role, 0) + n
        return n

    @property
    def total(self) -> int:
        return sum(self.by_role.values())


def run_workers(sources, provider, tracer, ledger):
    """Orchestrator delegates one source per worker; each worker extracts claims (one mock llm_call).

    Returns the flat, ordered list of claim artifacts handed back to the orchestrator.
    """
    claims: List[Dict[str, Any]] = []
    for source in sources:
        resp = provider.complete(worker_request(source))
        usage = resp.get("usage", {})
        ledger.add(WORKER, usage)
        extracted = json.loads(resp["content"])["claims"]
        for c in extracted:
            # Defensive: pin each claim to the source the worker was actually handed.
            claims.append({"text": c["text"], "source": source["id"], "worker": source["worker"]})
        tracer.emit(
            "llm_call",
            "ok",
            attributes={"role": WORKER, "worker": source["worker"], "source": source["id"],
                        "claims_extracted": len(extracted)},
            tokens={"input": int(usage.get("input_tokens", 0)), "output": int(usage.get("output_tokens", 0))},
        )
    return claims


def group_themes(claims, provider, tracer, ledger):
    """Orchestrator groups the collected claims into themes (one mock llm_call)."""
    resp = provider.complete(group_request(claims))
    usage = resp.get("usage", {})
    ledger.add(ORCHESTRATOR, usage)
    themes = json.loads(resp["content"])["themes"]
    tracer.emit(
        "llm_call",
        "ok",
        attributes={"role": ORCHESTRATOR, "step": "group_themes", "themes": len(themes)},
        tokens={"input": int(usage.get("input_tokens", 0)), "output": int(usage.get("output_tokens", 0))},
    )
    return themes


def synthesize(themes, claims, provider, tracer, ledger):
    """Orchestrator writes the final answer with per-claim source references (one mock llm_call)."""
    resp = provider.complete(synth_request(themes, claims))
    usage = resp.get("usage", {})
    ledger.add(ORCHESTRATOR, usage)
    synthesized = json.loads(resp["content"])
    tracer.emit(
        "llm_call",
        "ok",
        attributes={"role": ORCHESTRATOR, "step": "synthesize",
                    "synthesized_claims": len(synthesized["claims"])},
        tokens={"input": int(usage.get("input_tokens", 0)), "output": int(usage.get("output_tokens", 0))},
    )
    return synthesized


def evaluate_groundedness(synthesized, valid_source_ids, tracer):
    """Groundedness evaluator: every synthesized claim must cite >=1 source id present in the corpus.

    Returns (per_claim_results, grounded_count, total). Emits a decision event with the verdict.
    """
    valid = set(valid_source_ids)
    per_claim = []
    grounded = 0
    for i, claim in enumerate(synthesized["claims"]):
        cited = [s for s in claim.get("sources", []) if s in valid]
        is_grounded = len(cited) > 0
        if is_grounded:
            grounded += 1
        per_claim.append({"index": i, "text": claim["text"], "sources": claim.get("sources", []),
                          "grounded": is_grounded})
    total = len(per_claim)
    tracer.emit(
        "decision",
        "ok" if grounded == total else "rejected",
        attributes={"role": "evaluator", "step": "groundedness",
                    "grounded": grounded, "total": total},
    )
    return per_claim, grounded, total
