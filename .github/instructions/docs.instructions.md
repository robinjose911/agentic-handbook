---
applyTo: "docs/**"
---

# Editing guide chapters (`docs/`)

The guide is 19 chapters; the index is [`../../docs/README.md`](../../docs/README.md).

When editing a chapter:

- Start with `# <NN> · <Title>` and use `## ` sections; keep it focused.
- **Cite external claims** as `[text](../references.md#<id>)` — only ids defined in
  [`../../references.md`](../../references.md); citations must not dangle (the bijection is enforced).
- **Label volatile facts** (benchmark %, `$` figures, CVE ids, star/K counts) on the SAME line as a
  label keyword (`as of` / `verify` / `self-reported` / `illustrative` / `approximate` / `sanitized`).
- **Embed diagrams** as `![alt](../assets/diagrams/<file>.png)` — the file must exist (run the diagram
  step first if it doesn't).
- The AGENTIC mnemonic (ch01) and the capability-ladder table (ch12) are **canonical** in
  [`../../repo.config.json`](../../repo.config.json); keep them byte-consistent.

Verify with `.venv/bin/python tools/validate/all.py` before considering a chapter done.
