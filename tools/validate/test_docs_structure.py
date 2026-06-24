"""Validator: the 19 guide chapters exist with the required structure + diagram embeds (Stage 3.2–3.5)."""
import os
import re

import pytest

from catalog import CHAPTERS  # noqa: E402 (same dir) — single source of the 19-chapter list

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DOCS = os.path.join(REPO, "docs")
ASSETS = os.path.join(REPO, "assets")

# Chapters that must embed a specific diagram (by png filename fragment).
REQUIRED_EMBEDS = {
    "00-introduction": ["00-hero-decision-tree"],
    "01-mnemonic-and-systems-map": ["00-hero-decision-tree"],
    "02-decision-framework": ["00-hero-decision-tree"],
    "11-security-and-threat-model": ["10-lethal-trifecta-self-assessment"],
    "12-eu-ai-act-as-architecture": ["09-capability-tier-ladder"],
}


def _read(name: str) -> str:
    with open(os.path.join(DOCS, f"{name}.md"), encoding="utf-8") as fh:
        return fh.read()


def test_there_are_nineteen_chapters():
    assert len(CHAPTERS) == 19


@pytest.mark.parametrize("name", CHAPTERS)
def test_chapter_exists_with_title_and_sections(name):
    text = _read(name)
    assert text.lstrip().startswith("# "), f"{name}: must open with an H1 title"
    h2s = re.findall(r"^##\s+\S", text, flags=re.MULTILINE)
    assert len(h2s) >= 2, f"{name}: needs >=2 H2 sections (found {len(h2s)})"


def test_docs_directory_has_no_orphan_chapters():
    md = {f[:-3] for f in os.listdir(DOCS) if f.endswith(".md")}
    expected = set(CHAPTERS) | {"README"}  # README index allowed
    extra = md - expected
    assert not extra, f"unexpected docs/*.md: {sorted(extra)}"
    missing = set(CHAPTERS) - md
    assert not missing, f"missing chapters: {sorted(missing)}"


def test_guide_index_links_every_chapter():
    # The unit suite — not just the e2e spec — must catch a broken/incomplete guide table of contents.
    idx = _read("README")
    for slug in CHAPTERS:
        assert f"{slug}.md" in idx, f"docs/README.md does not link chapter {slug}"


def test_intro_says_what_this_is_not():
    assert re.search(r"what this is\s*not", _read("00-introduction"), re.I), \
        "00-introduction must contain a 'what this is not' section"


def test_anti_patterns_chapter_has_at_least_12_entries_with_fixes():
    fixes = _read("17-anti-patterns").count("**Fix:**")
    assert fixes >= 12, f"ch17 should have >=12 anti-patterns each with a **Fix:** (found {fixes})"


@pytest.mark.parametrize("name,fragments", REQUIRED_EMBEDS.items(), ids=list(REQUIRED_EMBEDS))
def test_chapter_embeds_required_diagram(name, fragments):
    text = _read(name)
    for frag in fragments:
        assert re.search(rf"!\[[^\]]*\]\([^)]*{re.escape(frag)}\.png\)", text), \
            f"{name}: must embed diagram {frag}.png"


@pytest.mark.parametrize("name", CHAPTERS)
def test_all_embedded_images_resolve(name):
    text = _read(name)
    for m in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", text):
        src = m.group(1)
        if src.startswith("http"):
            continue
        # Resolve relative to docs/.
        target = os.path.normpath(os.path.join(DOCS, src))
        assert os.path.exists(target), f"{name}: embedded image does not resolve: {src}"
