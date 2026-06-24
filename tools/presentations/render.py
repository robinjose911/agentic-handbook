#!/usr/bin/env python3
"""Render the board one-pager sources (presentations/src/*.md) to presentations/*.pdf, deterministically
(pure-Python PDF writer, no reportlab). Run:

    python tools/presentations/render.py
"""
from __future__ import annotations

import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

from pdf_writer import write_pdf  # noqa: E402

SRC = os.path.join(REPO, "presentations", "src")
OUT = os.path.join(REPO, "presentations")
WRAP = 90

# Helvetica/latin-1 has no em-dash or curly quotes; normalize to ASCII so they render (not as "?").
_PUNCT = {
    "—": "-", "–": "-", "’": "'", "‘": "'",
    "“": '"', "”": '"', "·": "-", "…": "...", "→": "->",
}


def _normalize_punct(s: str) -> str:
    for u, a in _PUNCT.items():
        s = s.replace(u, a)
    return s


def _wrap(s: str, n: int) -> list[str]:
    words, out, cur = s.split(" "), [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= n:
            cur = (cur + " " + w).strip()
        else:
            out.append(cur)
            cur = w
    if cur:
        out.append(cur)
    return out or [""]


def md_to_lines(md: str) -> list[str]:
    lines: list[str] = []
    for raw in md.splitlines():
        s = _normalize_punct(raw.rstrip())
        s = re.sub(r"^#{1,6}\s*", "", s)                  # heading markers
        s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)     # links -> text
        s = re.sub(r"[*_`>]", "", s)                       # emphasis / blockquote markers
        if not s.strip():
            lines.append("")
            continue
        lines.extend(_wrap(s, WRAP))
    return lines


def main() -> int:
    sources = sorted(glob.glob(os.path.join(SRC, "*.md")))
    if not sources:
        print("no presentation sources found", file=sys.stderr)
        return 1
    for src in sources:
        name = os.path.splitext(os.path.basename(src))[0]
        with open(src, encoding="utf-8") as fh:
            lines = md_to_lines(fh.read())
        out = os.path.join(OUT, f"{name}.pdf")
        write_pdf(out, lines)
        print(f"rendered presentations/{name}.pdf ({len(lines)} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
