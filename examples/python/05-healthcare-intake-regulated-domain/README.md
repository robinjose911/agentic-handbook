# Example 05 · Healthcare-intake, regulated domain (Python)

> ⚠️ **EDUCATIONAL ARCHITECTURE DEMO — NOT MEDICAL ADVICE.** This is a **synthetic / teaching example**
> of how to wire EU AI Act obligations into an agent's architecture. It is not a medical device, gives
> no medical advice, and uses only fictional data. Runs offline against the deterministic mock provider.

A regulated-domain intake agent: classify a patient message into an intent with a reason code, then
route it — and **every high-risk intent (emergency, medication) escalates to a human**. No clinical
decision is auto-handled. It shows the **T**rust surface as architecture:
[EU AI Act Articles 11/12/14](../../../docs/12-eu-ai-act-as-architecture.md) wired in, not bolted on.

## Run it

```bash
../../../.venv/bin/python run.py     # writes trace.jsonl, eval-report.json, receipt.json, audit-log.jsonl, technical-doc.json
../../../.venv/bin/python -m pytest  # the safety suite
```

Re-running is a no-op diff: deterministic (canned fixtures, a synthetic clock — no `datetime.now()`,
no `random`).

## The receipt (safety + audit)

Across the golden set, **5/5** must-escalate cases were honored — the **3** medical high-risk intents
(emergency / medication) plus **2** fail-safe cases (an unknown intent and an unparseable model
response) — with `noSilentAutoHandle` `True`. All **9** decisions were written to the immutable audit
log, and the run emitted **18** trace events conforming to
[`observability-event-schema.json`](../../../templates/observability-event-schema.json).

| EU AI Act article | How it's wired (as architecture) | Artifact |
|-------------------|----------------------------------|----------|
| **Art. 11** — technical documentation | generated *from* the system, not written about it | [`technical-doc.json`](technical-doc.json) |
| **Art. 12** — record-keeping / traceability | append-only audit log, one entry per decision | [`audit-log.jsonl`](audit-log.jsonl) |
| **Art. 14** — human oversight | every high-risk intent routes to `human-review` | [`receipt.json`](receipt.json) |

| Artifact | What it holds |
|----------|---------------|
| [`trace.jsonl`](trace.jsonl) | every classification + routing/escalation event |
| [`eval-report.json`](eval-report.json) | per-message safety results + the aggregate |
| [`audit-log.jsonl`](audit-log.jsonl) | the immutable per-decision record (Art. 12) |

## The safety invariant

The pytest suite proves the property a regulator cares about: **no high-risk intent is silently
auto-handled** — every emergency or medication message escalates, an unparseable/unknown intent
fails *safe* (escalates), and every decision leaves an audit entry. A change that weakened this would
fail the suite, not slip through.

The capability tier is **L1 (act-with-approval)**, but the health context raises the EU AI Act risk
floor to **high-risk** (Annex III) — see [chapter 12](../../../docs/12-eu-ai-act-as-architecture.md)
and the [capability-tier ladder](../../../templates/capability-tier-ladder.md).
