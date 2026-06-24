# FAQ

## Is this just another awesome-list?

No. An awesome-list points at other people's work; this handbook makes **decisions** and ships
**artifacts** you use on Monday — 19 chapters of opinionated guidance, 16 procurement-grade templates,
15 diagrams, and **five runnable examples with committed run receipts**. Every external claim is cited
in [`references.md`](references.md); a curated "further reading" list lives there too, but the value is
the decisions and the receipts, not the links.

## Why a European CPTO?

Because the [EU AI Act](docs/12-eu-ai-act-as-architecture.md) is treated as **architecture**, not a
compliance afterthought — Articles 11/12/14 as technical documentation, traceability, and human
oversight you build in. US-centric playbooks skip this. It is the explicit differentiator, woven
through the capability-tier ladder, chapter 12, the healthcare example, and the case studies.

## Do I need an API key to run the examples?

**No.** Every example runs **offline against a deterministic mock provider** — no API key, no network.
Responses are canned and hash-keyed; a re-run is a no-op diff. See [`examples/README.md`](examples/README.md).
An opt-in real-provider mode is documented but never runs in CI.

## Is the content vendor-neutral?

Yes. Patterns and templates are framework-agnostic. Where a vendor or tool is named (Claude, OpenAI,
LangGraph, MCP, …) it is as an example or a citation, not a dependency. The examples ship in TypeScript
and Python and take no framework you must adopt.

## How do I trust the numbers?

Two ways. The reference-example headline numbers are **machine-checked** against a committed
`receipt.json` (the prose can't drift from the run). And every volatile external fact — a benchmark
percentage, a star count, a CVE, a date — carries an _as of June 2026 — verify before relying_ label,
because the field moves fast. Re-verify before you rely on any of them.

## How do I contribute?

See [CONTRIBUTING.md](CONTRIBUTING.md) and open an issue with one of the templates (bug, pattern
proposal, anti-pattern proposal). The bar for a new pattern: it should be runnable against the mock
provider. Run `.venv/bin/python tools/validate/all.py` before you open a PR.
