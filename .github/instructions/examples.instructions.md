---
applyTo: "examples/**"
---

# Editing runnable examples (`examples/`)

The examples are the credibility engine: real mini-codebases that run **offline against the mock
provider**. The index is [`../../examples/README.md`](../../examples/README.md).

Rules for any example:

- **Mock provider only** in tests/CI — no API key, no network. An opt-in real-provider mode may be
  documented but never runs in CI.
- **Deterministic** — no `now()`, no RNG, no wall-clock; re-running an example is a no-op diff. Canned
  responses are keyed by a hash of `(system, messages, tools)`.
- **Commit the receipts** — each run emits a trace and an eval report, and a single receipt file holds
  the headline numbers. The example README's quoted numbers must equal the receipt (machine-checked).
- **Safety frames** — the healthcare example carries a loud "educational architecture demo, not medical
  advice" frame; high-risk intents must escalate to human review.

Run an example's own suite (Vitest / Pytest) plus the repo render-check before calling it done.
