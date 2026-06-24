# Copilot instructions — agentic-handbook

This repository is a vendor-neutral, CPTO-grade playbook for shipping reliable agents in production.
The seven surfaces of a reliable agent system spell **AGENTIC**: Autonomy, Goals, Evaluation, Networks,
Trust, Identity, Cost. When suggesting edits, keep the repo's hard rules.

## Hard rules

1. **Synthetic / safe only** — fictional orgs, toy datasets, no real customer data.
2. **Label volatile facts** — every star count, benchmark %, CVE, dollar figure, or date carries an
   `as of June 2026 — verify before relying` label.
3. **Cite external claims** — each one gets a row in [`../references.md`](../references.md); citations
   link `references.md#<id>` and must not dangle.
4. **One canonical mapping** — the AGENTIC↔chapter map and the capability-ladder↔EU-AI-Act risk-class
   mapping live once in [`../repo.config.json`](../repo.config.json); never retype them out of sync.
5. **Receipts match prose** — example headline numbers are machine-checked against committed receipts.

## How to verify a change

Run the unit validators and the render-check before proposing a change is done:

```bash
.venv/bin/python tools/validate/all.py
npm --prefix tests/e2e test
```

## Where things live

- Guide chapters: [`../docs/`](../docs/README.md) (start at
  [02 Decision framework](../docs/02-decision-framework.md)).
- Templates: [`../templates/`](../templates/README.md).
- Diagrams: Mermaid sources in `assets/diagrams/src/`, rendered to PNG.
- Path-scoped guidance: see [`instructions/`](instructions/docs.instructions.md).
