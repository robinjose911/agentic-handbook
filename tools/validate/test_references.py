"""Validator: references.md is a well-formed citation backbone and the citation BIJECTION holds —
every claim-backing row is cited by a chapter, and every chapter citation resolves to a defined row
(Stage 3.1). Rows under "## Further reading" are an exempt curated index. Live external-link checking
is deferred to Stage 7.1 (with the allowlist)."""
import glob
import os
import re

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
REFERENCES = os.path.join(REPO, "references.md")
DOCS = os.path.join(REPO, "docs")

ROW_RE = re.compile(r'<a id="([^"]+)"></a>\s*\[([^\]]+)\]\((https?://[^)]+)\)')
ANCHOR_RE = re.compile(r'<a id="([^"]+)"></a>')
VOLATILE_RE = re.compile(r"(\d+(?:\.\d+)?\s*%|\$\s*\d|CVE-\d{4}-\d+|\bstars?\b|\d[\d.,]*\s*[kKmM]\b)")
LABEL_RE = re.compile(r"(as of|verify|self-reported|illustrative|approximate|sanitized)", re.I)


def _refs_text():
    with open(REFERENCES, encoding="utf-8") as fh:
        return fh.read()


def _rows_with_section():
    """Return [(id, title, url, section_lower)] for every reference row, tracking its `## ` section."""
    rows, section = [], ""
    for line in _refs_text().splitlines():
        if line.startswith("## "):
            section = line[3:].strip().lower()
        m = ROW_RE.search(line)
        if m:
            rows.append((m.group(1), m.group(2), m.group(3), section))
    return rows


def _cited_ids():
    cited = set()
    for path in glob.glob(os.path.join(DOCS, "*.md")):
        with open(path, encoding="utf-8") as fh:
            cited |= set(re.findall(r"references\.md#([A-Za-z0-9\-]+)", fh.read()))
    return cited


def test_references_has_rows_with_unique_ids():
    rows = _rows_with_section()
    assert len(rows) >= 25, f"expected >=25 reference rows, found {len(rows)}"
    ids = [r[0] for r in rows]
    assert len(ids) == len(set(ids)), f"duplicate reference id(s): {[i for i in ids if ids.count(i) > 1]}"


def test_every_row_has_a_well_formed_link():
    for rid, title, url, _ in _rows_with_section():
        assert title.strip(), f"{rid}: empty link text"
        assert url.startswith("http"), f"{rid}: link is not http(s): {url}"


def test_volatile_figures_in_references_are_labeled():
    # Any reference line carrying a star count / % / $ / CVE / k-count must carry a label keyword.
    # Scans ANY line bearing an <a id=…> anchor (not just a "- " bullet), so an alt-bullet row is checked.
    for line in _refs_text().splitlines():
        if "<a id=" not in line:
            continue
        if VOLATILE_RE.search(line) and not LABEL_RE.search(line):
            raise AssertionError(f"unlabeled volatile figure in references row:\n  {line.strip()}")


def test_no_dangling_citations():
    defined = {r[0] for r in _rows_with_section()}
    cited = _cited_ids()
    dangling = sorted(cited - defined)
    assert not dangling, f"citations point at undefined reference ids: {dangling}"


def test_citation_bijection_every_claim_row_is_cited():
    rows = _rows_with_section()
    # Claim-backing rows = everything NOT under a "Further reading" section.
    claim_ids = {rid for rid, _t, _u, section in rows if "further reading" not in section}
    cited = _cited_ids()
    orphans = sorted(claim_ids - cited)
    assert not orphans, (
        "claim-backing reference rows are never cited by any chapter (move to '## Further reading' "
        f"if intentionally uncited): {orphans}"
    )
