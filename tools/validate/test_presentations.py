"""Validator: the three board one-pagers exist as sources, render to STRUCTURALLY VALID PDFs (real xref
offsets + stream lengths, so they open in a reader), the ladder one-pager carries the canonical mapping,
and the index links them (Stage 6.3)."""
import os
import re

import ladder  # noqa: E402 (same dir)

REPO = ladder.REPO
SRC = os.path.join(REPO, "presentations", "src")
OUT = os.path.join(REPO, "presentations")
EXPECTED = ["capability-tier-ladder", "rfp-template", "eu-ai-act-architecture"]


def test_sources_exist():
    for name in EXPECTED:
        assert os.path.exists(os.path.join(SRC, f"{name}.md")), f"missing presentations/src/{name}.md"


def _assert_pdf_opens(data: bytes, label: str):
    """Parse the xref table + stream lengths so a structurally-corrupt PDF (that still contains the
    right literals) fails — this is the 'won't open in a real reader' guard."""
    assert data.startswith(b"%PDF-"), f"{label}: no PDF header"
    m = re.search(rb"startxref\s+(\d+)\s+%%EOF\s*$", data)
    assert m, f"{label}: missing/!malformed startxref+EOF"
    xref_pos = int(m.group(1))
    assert data[xref_pos:xref_pos + 4] == b"xref", f"{label}: startxref does not point at the xref table"
    header = re.match(rb"xref\s+0\s+(\d+)\s+", data[xref_pos:])
    assert header, f"{label}: malformed xref header"
    count = int(header.group(1))
    # Each xref 'n' entry's byte offset must point at the matching '<obj> 0 obj' declaration.
    entries = re.findall(rb"(\d{10}) (\d{5}) (n|f) ?\n", data[xref_pos:])
    assert len(entries) == count, f"{label}: xref has {len(entries)} entries, header says {count}"
    for i, (off, _gen, kind) in enumerate(entries):
        if kind == b"n":
            offset = int(off)
            assert data[offset:].startswith(f"{i} 0 obj".encode()), (
                f"{label}: xref offset for object {i} does not point at '{i} 0 obj'"
            )
    # Every declared stream /Length must equal the actual stream byte count.
    for length, body in re.findall(rb"/Length (\d+) >>\s*stream\n(.*?)\nendstream", data, re.DOTALL):
        assert int(length) == len(body), f"{label}: a stream /Length ({int(length)}) != actual ({len(body)})"


def test_pdfs_render_valid_and_nonzero():
    for name in EXPECTED:
        path = os.path.join(OUT, f"{name}.pdf")
        assert os.path.exists(path), f"missing presentations/{name}.pdf (run render.py)"
        data = open(path, "rb").read()
        assert len(data) > 500, f"{name}.pdf is suspiciously small ({len(data)}B)"
        _assert_pdf_opens(data, f"{name}.pdf")


def test_ladder_one_pager_matches_canonical():
    with open(os.path.join(SRC, "capability-tier-ladder.md"), encoding="utf-8") as fh:
        ladder.assert_matches_canonical(fh.read(), "presentations/src/capability-tier-ladder.md")


def test_index_lists_every_pdf():
    with open(os.path.join(OUT, "README.md"), encoding="utf-8") as fh:
        idx = fh.read()
    for name in EXPECTED:
        assert f"{name}.pdf" in idx, f"presentations/README.md does not link {name}.pdf"
