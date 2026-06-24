"""Shared parser for the capability-tier-ladder ↔ EU AI Act risk-class mapping.

The mapping is canonical in repo.config.json. Every artifact that restates it — the
`capability-tier-ladder` template (Stage 2), the `09-capability-tier-ladder` diagram (Stage 1), ch12
(Stage 3), the README (Stage 6), and the ladder one-pager (Stage 6) — must agree. This module gives
the canonical mapping and a tolerant markdown-table parser so each stage can assert its copy matches.
"""
import functools
import json
import os
import re

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Longest / most-specific first so "high-risk" wins over a bare "high" and "prohibited" is matched
# before anything else.
RISK_CLASSES = ["prohibited", "high-risk", "limited", "minimal"]


@functools.lru_cache(maxsize=1)
def canonical_ladder() -> list[dict]:
    """The canonical L0–L4 mapping from repo.config.json (read once per run; config is immutable)."""
    with open(os.path.join(REPO, "repo.config.json"), encoding="utf-8") as fh:
        cfg = json.load(fh)
    return [
        {"tier": t["tier"], "name": t["name"], "euRiskClass": t["euRiskClass"], "criteria": t["criteria"]}
        for t in cfg["capabilityLadder"]
    ]


def normalize_risk(cell: str) -> str:
    """Extract the canonical risk class from a table cell, tolerating extra words
    (e.g. 'High-risk (Annex III)' -> 'high-risk')."""
    c = cell.strip().lower()
    for rc in RISK_CLASSES:
        if rc in c:
            return rc
    return c


def parse_ladder_table(markdown_text: str) -> list[dict]:
    """Parse the first markdown table that maps tiers to risk classes.

    Returns a list of {tier, name, risk} dicts for the L0–L4 rows. Column positions are found by
    header keyword (tier / name / risk), so artifacts may add columns or reorder them.
    """
    lines = markdown_text.splitlines()
    for i, line in enumerate(lines):
        if "|" not in line:
            continue
        header = [c.strip() for c in line.strip().strip("|").split("|")]
        low = [h.lower() for h in header]
        # A ladder table's header has a tier column and an EU-risk column.
        tier_idx = next((j for j, h in enumerate(low) if "tier" in h), None)
        # Pick the EU risk-class column specifically — prefer a header naming the EU/AI-Act/risk-class,
        # else the LAST 'risk' column — so an earlier 'Risk appetite'/'Residual risk' column never wins.
        risk_cols = [j for j, h in enumerate(low) if "risk" in h]
        risk_idx = next(
            (j for j in risk_cols if any(k in low[j] for k in ("risk class", "ai act", "eu"))),
            risk_cols[-1] if risk_cols else None,
        )
        name_idx = next((j for j, h in enumerate(low) if "name" in h), None)
        criteria_idx = next((j for j, h in enumerate(low) if "criteria" in h), None)
        if tier_idx is None or risk_idx is None:
            continue
        # Next line must be the markdown table separator (---).
        if i + 1 >= len(lines) or not re.match(r"^\s*\|?[\s:|-]+\|?\s*$", lines[i + 1]):
            continue
        rows = []
        for row_line in lines[i + 2:]:
            if "|" not in row_line:
                break
            cells = [c.strip() for c in row_line.strip().strip("|").split("|")]
            if tier_idx >= len(cells) or not re.match(r"^L\d", cells[tier_idx]):
                if rows:
                    break
                continue
            tier = re.match(r"^(L\d)", cells[tier_idx]).group(1)
            # name / criteria are None (not "") when the table lacks that column, so those checks skip.
            name = cells[name_idx] if name_idx is not None and name_idx < len(cells) else None
            criteria = cells[criteria_idx] if criteria_idx is not None and criteria_idx < len(cells) else None
            risk = normalize_risk(cells[risk_idx]) if risk_idx < len(cells) else ""
            rows.append({"tier": tier, "name": name, "criteria": criteria, "risk": risk})
        if rows:
            return rows
    return []


def assert_matches_canonical(markdown_text: str, source_label: str) -> None:
    """Assert a markdown artifact's ladder table matches the canonical tier→risk mapping.

    The tier→risk mapping is checked strictly. The tier name is checked only when the table has a name
    column (a correct Tier|Risk two-column restatement is not failed for lacking a Name column).
    """
    parsed = parse_ladder_table(markdown_text)
    assert parsed, f"{source_label}: no capability-ladder table found"
    by_tier = {r["tier"]: r for r in parsed}
    for c in canonical_ladder():
        row = by_tier.get(c["tier"])
        assert row is not None, f"{source_label}: missing tier {c['tier']}"
        assert row["risk"] == c["euRiskClass"], (
            f"{source_label}: {c['tier']} maps to '{row['risk']}', canonical is '{c['euRiskClass']}'"
        )
        if row["name"] is not None:
            assert c["name"].lower() in row["name"].lower(), (
                f"{source_label}: {c['tier']} name '{row['name']}' "
                f"does not contain canonical '{c['name']}'"
            )
        # When the table carries a criteria column, the criteria text must match canonical verbatim
        # (normalized for whitespace) — the substance of each tier can't drift silently.
        if row.get("criteria") is not None:
            got = " ".join(row["criteria"].split())
            want = " ".join(c["criteria"].split())
            assert got == want, (
                f"{source_label}: {c['tier']} criteria drifted from canonical.\n  got:  {got}\n  want: {want}"
            )
