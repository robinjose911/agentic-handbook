"""Validator: ch01's AGENTIC mnemonic table — the 7 surfaces, their order, and the chapters each maps
to — matches repo.config.json exactly (Stage 3.2). Binds each chapter to ITS surface row (not a
whole-file substring), so a surface pointing at the wrong chapter fails. Re-checked vs the README in
Stage 6."""
import json
import os
import re

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CH01 = os.path.join(REPO, "docs", "01-mnemonic-and-systems-map.md")


def _config_surfaces():
    with open(os.path.join(REPO, "repo.config.json"), encoding="utf-8") as fh:
        return json.load(fh)["mnemonic"]["surfaces"]


def _ch01():
    with open(CH01, encoding="utf-8") as fh:
        return fh.read()


def _parse_mnemonic_table():
    """Parse the AGENTIC table by header keyword. Returns rows of {letter, surface, maps}."""
    lines = _ch01().splitlines()
    header_idx, cols = None, {}
    for i, line in enumerate(lines):
        low = line.lower()
        if "|" in line and "surface" in low and "map" in low:
            header = [c.strip().lower() for c in line.strip().strip("|").split("|")]
            cols = {
                "letter": next((j for j, h in enumerate(header) if "letter" in h), None),
                "surface": next((j for j, h in enumerate(header) if "surface" in h), None),
                "maps": next((j for j, h in enumerate(header) if "map" in h), None),
            }
            header_idx = i
            break
    if header_idx is None or cols["surface"] is None or cols["maps"] is None:
        return []
    rows = []
    for line in lines[header_idx + 2:]:
        if "|" not in line:
            break
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cols["surface"] >= len(cells) or not cells[cols["surface"]]:
            continue
        surface = re.sub(r"[*`]", "", cells[cols["surface"]]).strip()
        rows.append({
            "letter": re.sub(r"[*`]", "", cells[cols["letter"]]).strip() if cols["letter"] is not None else "",
            "surface": surface,
            "maps": cells[cols["maps"]] if cols["maps"] < len(cells) else "",
        })
    return rows


def test_ch01_spells_agentic():
    assert "AGENTIC" in _ch01()


def test_ch01_table_surfaces_match_config_in_order():
    table = _parse_mnemonic_table()
    assert table, "ch01 must contain an AGENTIC table with Surface + Maps columns"
    assert [r["surface"] for r in table] == [s["name"] for s in _config_surfaces()], (
        "ch01 table surfaces (or their order) do not match repo.config.json"
    )
    assert [r["letter"] for r in table] == [s["letter"] for s in _config_surfaces()], (
        "ch01 table letters do not match repo.config.json (AGENTIC)"
    )


def test_ch01_each_row_maps_to_exactly_its_canonical_chapters():
    table = {r["surface"]: r["maps"] for r in _parse_mnemonic_table()}
    for s in _config_surfaces():
        cell = table.get(s["name"], "")
        slugs_in_cell = set(re.findall(r"\d{2}-[a-z0-9-]+", cell))
        expected = set(s["chapters"])
        assert slugs_in_cell == expected, (
            f"ch01 surface '{s['name']}' maps to {sorted(slugs_in_cell)}, "
            f"canonical is {sorted(expected)}"
        )
