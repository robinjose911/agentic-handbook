---
name: Bug report
about: A broken link, a failing validator, a wrong fact, or a rendering issue
title: "[bug] "
labels: bug
---

## What's wrong

<!-- A clear description. If it's a wrong/stale fact, quote it and link the source that contradicts it. -->

## Where

- File / chapter / template:
- Link, if applicable:

## Expected vs actual

<!-- What you expected, and what you saw. -->

## To reproduce (for tooling/validator bugs)

```bash
# the command you ran
.venv/bin/python tools/validate/all.py
```

## Checklist

- [ ] I checked this isn't already a labeled `_as of June 2026 — verify before relying_` volatile fact.
- [ ] I ran the validators locally (if a tooling bug).
