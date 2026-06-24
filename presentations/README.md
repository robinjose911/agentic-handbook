# Presentations

Three board-ready one-pagers (PDF), rendered deterministically from the markdown sources in
[`src/`](src/capability-tier-ladder.md) via `tools/presentations/render.py` (pure-Python, no
dependencies). They signal CPTO seriousness in a procurement or board review.

| One-pager | What it's for |
|-----------|---------------|
| [Capability tier ladder](capability-tier-ladder.pdf) | The L0–L4 autonomy ladder mapped to EU AI Act risk classes. |
| [Agent vendor RFP](rfp-template.pdf) | The questions to ask before signing an agent-platform contract. |
| [EU AI Act as architecture](eu-ai-act-architecture.pdf) | Articles 11/12/14 as components you build in. |

To regenerate after editing a source: `.venv/bin/python tools/presentations/render.py`.
