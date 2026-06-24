"""Validator (Stage 7.3): the EU AI Act framing appears in all SIX places the proposal requires, the
article->component mapping in ch12 is correct, and the capability-ladder->risk-class mapping is
identical across the five artifacts that restate it."""
import os
import re

import ladder  # noqa: E402 (same dir)

REPO = ladder.REPO

# The six places the EU lens must appear (proposal §13).
SIX_PLACES = {
    "README": "README.md",
    "ch01 Trust surface": "docs/01-mnemonic-and-systems-map.md",
    "capability-tier-ladder template": "templates/capability-tier-ladder.md",
    "ch12": "docs/12-eu-ai-act-as-architecture.md",
    "healthcare example 05": "examples/python/05-healthcare-intake-regulated-domain/README.md",
    "case studies ch18": "docs/18-case-studies.md",
}

# The five artifacts that restate the L0-L4 -> risk-class mapping (markdown tables + the diagram).
LADDER_TABLES = [
    "templates/capability-tier-ladder.md",
    "docs/12-eu-ai-act-as-architecture.md",
    "README.md",
    "presentations/src/capability-tier-ladder.md",
]
DIAGRAM_SRC = "assets/diagrams/src/09-capability-tier-ladder.mmd"

ARTICLE_COMPONENT = {
    "article 11": ["technical documentation"],
    "article 12": ["record-keeping", "traceability", "logging"],
    "article 14": ["human oversight"],
}


def _read(rel):
    with open(os.path.join(REPO, rel), encoding="utf-8") as fh:
        return fh.read()


def test_eu_framing_in_all_six_places():
    missing = [name for name, rel in SIX_PLACES.items() if "eu ai act" not in _read(rel).lower()]
    assert not missing, f"EU AI Act framing missing from: {missing}"


def test_ch12_binds_each_article_to_its_component():
    lines = _read("docs/12-eu-ai-act-as-architecture.md").lower().splitlines()
    for art, comps in ARTICLE_COMPONENT.items():
        matched = [ln for ln in lines if art in ln]
        assert matched, f"ch12 must cover {art}"
        assert any(any(c in ln for c in comps) for ln in matched), (
            f"ch12: {art} not bound to its component {comps} on the same line"
        )


def test_ch12_names_all_four_risk_classes():
    text = _read("docs/12-eu-ai-act-as-architecture.md").lower()
    for risk in ["minimal", "limited", "high-risk", "prohibited"]:
        assert risk in text, f"ch12 must reference '{risk}'"


def test_ladder_mapping_identical_across_all_five_artifacts():
    # The four markdown tables.
    for rel in LADDER_TABLES:
        ladder.assert_matches_canonical(_read(rel), rel)
    # The diagram: each tier node carries its canonical name + risk (and no other risk class).
    src = _read(DIAGRAM_SRC)
    for c in ladder.canonical_ladder():
        m = re.search(rf'{c["tier"]}\["([^"]*)"\]', src)
        assert m, f"diagram missing node for {c['tier']}"
        node = m.group(1)
        assert c["name"] in node and c["euRiskClass"] in node, (
            f"diagram {c['tier']} node not canonical"
        )
        wrong = [rc for rc in ladder.RISK_CLASSES if rc != c["euRiskClass"] and rc in node]
        assert not wrong, f"diagram {c['tier']} node names wrong risk class(es) {wrong}"
