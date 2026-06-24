"""Validator: the README hero is built from repo.config.json and stays consistent — the AGENTIC block
matches config, the capability-ladder summary matches canonical, the buttons resolve, the banner is the
real asset, and the prose avoids AI-catchphrase tells (Stage 6.2)."""
import json
import os

import ladder  # noqa: E402 (same dir) — canonical ladder + assert_matches_canonical

REPO = ladder.REPO
README = os.path.join(REPO, "README.md")

AI_CATCHPHRASES = [
    "dive into", "in today's fast-paced", "unleash", "game-chang", "harness the power",
    "elevate your", "take it to the next level", "look no further", "supercharge", "delve into",
    "seamless integration", "revolutionize",
]


def _readme():
    with open(README, encoding="utf-8") as fh:
        return fh.read()


def _config():
    with open(os.path.join(REPO, "repo.config.json"), encoding="utf-8") as fh:
        return json.load(fh)


def _parse_agentic_table():
    """Parse the README AGENTIC table -> [(letter, name)] in row order."""
    import re

    lines = _readme().splitlines()
    rows, in_table = [], False
    for line in lines:
        low = line.lower()
        if "|" in line and "surface" in low and ("covers" in low or "what" in low):
            in_table = True
            continue
        if in_table:
            if "|" not in line:
                break
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            letter = re.sub(r"[*`]", "", cells[0]).strip() if cells else ""
            if not re.fullmatch(r"[A-Z]", letter):  # skip the separator row / non-letter rows
                continue
            name = cells[1].strip() if len(cells) > 1 else ""
            rows.append((letter, name))
    return rows


def test_readme_agentic_table_binds_letters_to_names_in_order():
    table = _parse_agentic_table()
    canon = [(s["letter"], s["name"]) for s in _config()["mnemonic"]["surfaces"]]
    assert table == canon, f"README AGENTIC table {table} != canonical {canon}"
    assert "AGENTIC" in _readme()


def test_readme_capability_ladder_matches_canonical():
    ladder.assert_matches_canonical(_readme(), "README.md")


def test_readme_banner_is_the_real_asset():
    text = _readme()
    assert "](assets/banner.png)" in text, "README must embed assets/banner.png"
    with open(os.path.join(REPO, "assets", "manifest.json"), encoding="utf-8") as fh:
        banner = next(s for s in json.load(fh)["slots"] if s["id"] == "banner")
    assert banner["status"] == "real", "banner slot must be real before the README ships"
    assert os.path.exists(os.path.join(REPO, "assets", "banner.png"))


def test_readme_buttons_and_cta_resolve():
    text = _readme()
    cfg = _config()
    # Check each button by its LABEL + href together (an href like templates/README.md also appears in
    # the "What's inside" list, so an href-only check wouldn't catch a deleted hero button).
    for b in cfg["buttons"]:
        assert b["label"] in text, f"README missing hero button '{b['label']}'"
        assert b["href"] in text, f"README missing link {b['href']} for button '{b['label']}'"
        assert os.path.exists(os.path.join(REPO, b["href"])), f"button target missing on disk: {b['href']}"
    cta = cfg["decisionTreeCta"]
    assert cta["href"] in text and os.path.exists(os.path.join(REPO, cta["href"])), \
        "README decision-tree CTA missing or unresolved"


def test_readme_avoids_ai_catchphrases():
    low = _readme().lower()
    hits = [p for p in AI_CATCHPHRASES if p in low]
    assert not hits, f"README contains AI-catchphrase tells: {hits}"
