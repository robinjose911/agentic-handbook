# AGENTS.md

How coding assistants should work in this repository. (The git-ignored `CLAUDE.md` is a private build
brief and is **not** part of the shipped AI-native set — `AGENTS.md`, `llms.txt`, and the
`.github/` instruction tree are.)

## What this repo is

A vendor-neutral, CPTO-grade playbook for shipping reliable agents in production. The seven surfaces of
a reliable agent system spell **AGENTIC**: Autonomy, Goals, Evaluation, Networks, Trust, Identity, Cost.
See [`llms.txt`](llms.txt) for the full map of the 19 chapters and 16 templates.

## Hard rules (do not violate)

1. **Synthetic / safe only.** Fictional orgs, toy datasets. No real customer data, no private code.
2. **Receipts match prose.** Every runnable example executes against the deterministic mock provider and
   commits its trace + eval report; headline numbers are machine-checked against the receipt.
3. **Label volatile facts.** Star counts, benchmark percentages, CVEs, dollar figures, and dates carry a
   label (`as of June 2026 — verify before relying`). Enforced by `tools/validate/test_labels.py`.
4. **Cite every external claim.** Each one has a row in [`references.md`](references.md); the citation
   bijection is enforced by `tools/validate/test_references.py`.
5. **One canonical mapping.** The AGENTIC↔chapter map and the capability-ladder↔EU-AI-Act mapping live
   once in `repo.config.json` and must agree everywhere they appear.

## Build & test commands

The whole unit suite (Python validators plus the Node preview + mock-LLM checks):

```bash
.venv/bin/python tools/validate/all.py
```

Render the local preview (stands in for GitHub's renderer) and serve it:

```bash
node tools/preview/build.mjs
node tools/preview/serve.mjs        # http://localhost:4321
```

Run the integration render-checks (Playwright project lives in `tests/e2e`):

```bash
npm --prefix tests/e2e test
```

The five runnable examples each ship their own suite (Vitest / Pytest) and run **offline against the
mock provider** — no API key, no network. See [`examples/README.md`](examples/README.md) for the
per-example run commands (they land with the example code).

## Conventions

- Diagrams are Mermaid sources in `assets/diagrams/src/` rendered to PNG; the manifest
  (`assets/manifest.json`) is the source of truth for every visual slot.
- Markdown links to a `.md` file or a directory are how cross-references work; a linked directory must
  contain a `README.md`.
- Tool-level TypeScript runs directly via `node --experimental-strip-types`; keep it erasable-only.
