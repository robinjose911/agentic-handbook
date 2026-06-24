# Contributing

> 🚧 Skeleton — the full contribution guide lands in Stage 7.

Thanks for your interest in the **agentic-handbook**. This is a vendor-neutral, CPTO-grade
playbook for shipping reliable agents in production.

## Ground rules (carried from the build conventions)

1. **Synthetic / safe only.** Fictional orgs and toy datasets. No real customer data, no private code.
2. **Receipts must match prose.** Every reference example runs deterministically against the mock
   provider and commits its trace + eval report; headline numbers are machine-checked against the receipt.
3. **Label volatile facts.** Star counts, benchmark percentages, CVEs, dollar figures, and dates sit in a
   labeled span (`as of June 2026 — verify before relying`).
4. **Every external claim has a citation row** in `references.md`.

## How to run the tests

See `AGENTS.md` for the full command list. In short:

```bash
.venv/bin/python tools/validate/all.py        # unit validators
npx playwright test tests/e2e/                 # integration render-checks
```
