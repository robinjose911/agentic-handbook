---
applyTo: "assets/diagrams/**"
---

# Editing diagrams (`assets/diagrams/`)

The 15 diagrams are Mermaid sources rendered to PNG. The gallery is
[`../../assets/diagrams/README.md`](../../assets/diagrams/README.md).

Rules:

- **Edit the source, not the PNG.** Sources live in `assets/diagrams/src/` as `.mmd`; each starts with
  the house theme init block + the shared classDefs.
- **Re-render after editing.** Render the `.mmd` to its PNG, then run the manifest sync so
  `assets/manifest.json` records the real rendered dimensions and marks the slot `real`.
- **The manifest is the source of truth** for every visual slot; the render-checks assert each image
  against the dimensions recorded there.
- **The `09-capability-tier-ladder` diagram is load-bearing** — each tier node must carry its canonical
  name and EU AI Act risk class, consistent with [`../../repo.config.json`](../../repo.config.json).
  A per-tier drift fails the consistency gate.

Verify with `.venv/bin/python tools/validate/all.py` (the diagram + manifest validators) before done.
