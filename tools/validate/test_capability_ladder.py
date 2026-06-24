"""Validator (the headline consistency gate): the capability-tier-ladder ↔ EU AI Act mapping is the
same in the template, the diagram source, the HITL policy, and repo.config.json (Stage 2.2). The
global scan also gates any future restatement (ch12, README, one-pager) automatically."""
import glob
import os
import re

import ladder  # noqa: E402  (same dir)

REPO = ladder.REPO
TEMPLATE = os.path.join(REPO, "templates", "capability-tier-ladder.md")
DIAGRAM_SRC = os.path.join(REPO, "assets", "diagrams", "src", "09-capability-tier-ladder.mmd")


def test_canonical_ladder_is_l0_to_l4():
    canon = ladder.canonical_ladder()
    assert [c["tier"] for c in canon] == ["L0", "L1", "L2", "L3", "L4"]
    assert {c["euRiskClass"] for c in canon} <= set(ladder.RISK_CLASSES)


def test_template_table_matches_canonical():
    with open(TEMPLATE, encoding="utf-8") as fh:
        ladder.assert_matches_canonical(fh.read(), "capability-tier-ladder.md")


def test_diagram_node_binds_each_tier_to_its_canonical_name_and_risk():
    # The 09 diagram is not a markdown table, but each tier NODE must carry its own name + risk class.
    # Binding the check to the node (not a whole-file substring) catches a per-tier swap, e.g. L0's
    # node reading 'EU: prohibited' while 'prohibited' still appears elsewhere in the file.
    with open(DIAGRAM_SRC, encoding="utf-8") as fh:
        src = fh.read()
    for c in ladder.canonical_ladder():
        # Capture the node text for this tier: `L0["...node text..."]`.
        m = re.search(rf'{c["tier"]}\["([^"]*)"\]', src) or re.search(rf'{c["tier"]}\[([^\]]*)\]', src)
        assert m, f"diagram: no node found for tier {c['tier']}"
        node = m.group(1)
        assert c["name"] in node, f"diagram: {c['tier']} node missing name '{c['name']}'"
        assert c["euRiskClass"] in node, (
            f"diagram: {c['tier']} node '{node}' does not carry canonical risk '{c['euRiskClass']}'"
        )
        # And no OTHER risk class may appear in this tier's node (catches a swap to a valid-but-wrong class).
        wrong = [rc for rc in ladder.RISK_CLASSES if rc != c["euRiskClass"] and rc in node]
        assert not wrong, f"diagram: {c['tier']} node also names wrong risk class(es) {wrong}"


def test_every_ladder_table_in_the_repo_matches_canonical():
    """Any markdown table that restates the L0–L4 ladder (anywhere in templates/ or docs/) is gated —
    so a 4th/5th copy can never drift unnoticed (hard rule #4)."""
    md_files = glob.glob(os.path.join(REPO, "templates", "**", "*.md"), recursive=True)
    md_files += glob.glob(os.path.join(REPO, "docs", "**", "*.md"), recursive=True)
    md_files += [os.path.join(REPO, "README.md")]  # the hero ladder summary (Stage 6)
    checked = []
    for path in sorted(set(md_files)):
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        rows = ladder.parse_ladder_table(text)
        tiers = {r["tier"] for r in rows}
        if {"L0", "L4"} <= tiers:  # only gate tables that are actually a full capability ladder
            ladder.assert_matches_canonical(text, os.path.relpath(path, REPO))
            checked.append(os.path.relpath(path, REPO))
    # Every known artifact that restates the ladder MUST be parsed + gated. Asserting explicit
    # membership closes the "silently skipped because the header drifted unparseable" blind spot:
    # if any of these renames its risk-class column or drops a tier, it falls out of `checked` and
    # this assertion fails loudly instead of the divergent table shipping unchecked.
    for required in [
        "templates/capability-tier-ladder.md",
        "templates/human-in-the-loop-policy.md",
        "docs/12-eu-ai-act-as-architecture.md",
        "README.md",
    ]:
        assert required in checked, (
            f"{required} restates the capability ladder but was not gated — is its table parseable "
            f"(a 'Tier' column + an 'EU AI Act risk class' column, with L0 and L4 rows)?"
        )
