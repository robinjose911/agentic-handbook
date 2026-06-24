"""Validator: every volatile fact in the guide sits on a labeled line (Stage 3.x; full sweep in 7.2).

High-signal volatile patterns (benchmark/savings %, dollar figures, CVE ids) must share their line
with a label keyword (as of / verify / self-reported / illustrative / approximate). This enforces the
label-and-cite accuracy stance without fighting benign numbers (chapter/article numbers, L0–L4)."""
import glob
import os
import re

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DOCS = os.path.join(REPO, "docs")

# Volatile patterns that must sit on a labeled line: benchmark/savings %, dollar figures, CVE ids,
# star counts (a NUMBER before "stars", so "north star" prose isn't a false positive), K/M-suffixed
# counts, and time-duration figures like the METR horizon (CLAUDE.md hard-rule #3 names it explicitly).
VOLATILE_RE = re.compile(
    r"(\d+(?:\.\d+)?\s*%"
    r"|\$\s*\d[\d,]*"
    r"|CVE-\d{4}-\d+"
    r"|\d[\d.,]*\s*[kKmM]?\s*stars?\b"
    r"|\d[\d.,]*\s*[kKmM]\b"
    r"|\d+(?:\.\d+)?\s*-?\s*(?:hours?|hrs?)\b)"
)
LABEL_RE = re.compile(r"(as of|verify|self-reported|illustrative|approximate|sanitized)", re.I)
# A markdown image whose target is an external URL (a shields.io / GitHub-actions badge) — its
# URL-encoded % is not a volatile fact, so skip the whole image line (and ONLY such lines).
BADGE_LINE_RE = re.compile(r"!\[[^\]]*\]\(https?://")


def _unlabeled_volatile_lines(text: str) -> list[str]:
    out = []
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        # Skip only badge IMAGE lines (their URL-encoded % is not a volatile fact). A prose line that
        # merely mentions "shields.io" is still scanned, so a real $/% fact there can't hide.
        if BADGE_LINE_RE.search(line):
            continue
        if VOLATILE_RE.search(line) and not LABEL_RE.search(line):
            out.append(line.strip())
    return out


def _scan_targets():
    # Shipped prose where a volatile EXTERNAL fact (benchmark %, CVE, star/K count, $ figure) could hide
    # unlabeled: the guide + the root README/FAQ. Templates use {{placeholders}} + table-level
    # "illustrative" labels (a different, appropriate convention), and example READMEs carry exact
    # receipt numbers machine-checked by the prose-vs-receipt gate — neither is scanned per-line here.
    targets = glob.glob(os.path.join(DOCS, "*.md"))
    targets += [os.path.join(REPO, "README.md"), os.path.join(REPO, "FAQ.md")]
    return sorted(t for t in targets if os.path.exists(t))


def test_every_volatile_fact_in_shipped_prose_is_labeled():
    offenders = {}
    for path in _scan_targets():
        bad = _unlabeled_volatile_lines(open(path, encoding="utf-8").read())
        if bad:
            offenders[os.path.relpath(path, REPO)] = bad
    assert not offenders, "unlabeled volatile facts:\n" + "\n".join(
        f"  {f}: {lines}" for f, lines in offenders.items()
    )
