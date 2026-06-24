# Examples

Five runnable reference examples — the credibility engine. Each is a real mini-codebase that executes
**deterministically against the mock provider** (no API key, no network) and commits its run
`trace.jsonl`, `eval-report.json`, and a `receipt.json` whose headline numbers are machine-checked
against the prose (`tools/validate/test_examples.py`). Re-running any example is a no-op diff.

Every example is **synthetic / teaching** only.

| # | Example | Lang | Pattern it owns | Receipt headline |
|---|---------|------|-----------------|------------------|
| 1 | [support-triage agent](typescript/01-support-triage-agent/README.md) | TypeScript | chaining → routing → evaluator (structured output, basic HITL) | classification pass-rate 100% (6/6) |
| 2 | [outbound-lead workflow agent](typescript/02-outbound-lead-workflow-agent/README.md) | TypeScript | outer durable workflow + inner agent loop, HITL gates, pre-execution budget cap | budget honored, max lead ≤ cap |
| 3 | [evaluator-optimizer](typescript/03-evaluator-optimizer-self-improving/README.md) | TypeScript | generate → critique → revise to a rubric gate | score climb to ≥ gate |
| 4 | [research-synthesis multi-agent](python/04-research-synthesis-multi-agent/README.md) | Python | orchestrator-worker with explicit artifact handoff | groundedness 100% + per-role token split |
| 5 | [healthcare-intake (regulated)](python/05-healthcare-intake-regulated-domain/README.md) | Python | EU AI Act Art. 11/12/14 wiring — _educational architecture demo, not medical advice_ | every high-risk intent escalated |

## How they run

- **TypeScript (01–03):** `npm install && npm run run && npm test` in the example dir. The entrypoint
  runs under `node --experimental-strip-types` (no build step); tests use Vitest.
- **Python (04–05):** `../../../.venv/bin/python run.py` then `pytest` in the example dir — stdlib only,
  no install.

Each example imports the shared [mock LLM provider](../tools/mock-llm/) (TS + Python bindings that share
a byte-identical hash), so one recorded fixture works for both languages. An unrecorded request throws
loudly rather than hitting a real API.

See [chapter 03 — the pattern catalog](../docs/03-pattern-catalog.md) for the patterns these examples
own, and [chapter 13 — evaluations](../docs/13-evaluations.md) for the eval-driven loop they embody.
