"""Validator: any worked cost/savings math in the cost-stack chapter recomputes from stated inputs
(Stage 3.5). A figure that drifts from its own arithmetic is a failing test."""
import os
import re

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CH15 = os.path.join(REPO, "docs", "15-cost-stack.md")

# A machine-checkable savings table: | Layer | Base $ | Effective $ | Savings % |
# The validator recomputes savings = round((base - effective) / base * 100).
MONEY = r"\$?\s*([0-9]+(?:\.[0-9]+)?)"
ROW_RE = re.compile(
    r"\|[^|]*\|\s*" + MONEY + r"\s*\|\s*" + MONEY + r"\s*\|\s*([0-9]+(?:\.[0-9]+)?)\s*%\s*\|"
)


def _decimals(s: str) -> int:
    return len(s.split(".")[1]) if "." in s else 0


def test_cost_savings_table_recomputes():
    with open(CH15, encoding="utf-8") as fh:
        text = fh.read()
    rows = ROW_RE.findall(text)
    assert rows, "ch15 must carry a machine-checkable savings table (| Layer | Base $ | Effective $ | Savings % |)"
    for base, effective, stated in rows:
        base_f, eff_f = float(base), float(effective)
        assert base_f > 0, f"base cost must be > 0 in row ({base}, {effective}, {stated})"
        # Recompute at the stated value's own precision and require an EXACT match — no tolerance,
        # so a figure off by even one point fails (the lint's whole promise).
        computed = round((base_f - eff_f) / base_f * 100, _decimals(stated))
        assert computed == float(stated), (
            f"savings drift: stated {stated}% but ({base}-{effective})/{base} = {computed}%"
        )
