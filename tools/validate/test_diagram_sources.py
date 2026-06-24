"""Validator: the 15 Mermaid sources exist, carry the house theme, and structurally lint (Stage 1.1).

A full Mermaid parse needs a browser (mmdc/Chromium); the actual render is validated by Stage 1.2
(every source rendered to a real PNG via kroki). Here we do a deterministic structural lint plus the
capability-ladder seed check.
"""
import json
import os
import re

import pytest

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.path.join(REPO, "assets", "diagrams", "src")

EXPECTED = [
    "00-hero-decision-tree", "01-agent-loop", "02-workflow-vs-agent", "03-router-pattern",
    "04-planner-executor", "05-supervisor-worker", "06-evaluator-optimizer", "07-tool-approval-flow",
    "08-eval-observability-loop", "09-capability-tier-ladder", "10-lethal-trifecta-self-assessment",
    "11-mcp-vs-a2a-stack", "12-codeact-decision", "13-mcp-threat-model-attack-tree",
    "14-durable-execution-outer-workflow",
]

DIAGRAM_TYPES = ("flowchart", "graph", "sequenceDiagram", "stateDiagram-v2", "stateDiagram",
                 "classDiagram", "erDiagram", "journey", "gantt")


def _read(name: str) -> str:
    with open(os.path.join(SRC, f"{name}.mmd"), encoding="utf-8") as fh:
        return fh.read()


def test_all_fifteen_sources_exist():
    found = sorted(f[:-4] for f in os.listdir(SRC) if f.endswith(".mmd"))
    assert found == sorted(EXPECTED), f"source set mismatch: {found}"


@pytest.mark.parametrize("name", EXPECTED)
def test_source_has_theme_block(name):
    text = _read(name)
    assert "%%{init:" in text, f"{name}: missing the %%{{init}} theme block"
    assert '"theme": "base"' in text, f"{name}: missing the base theme"


@pytest.mark.parametrize("name", EXPECTED)
def test_source_declares_a_diagram_type(name):
    text = _read(name)
    # Strip the init block, then the first non-empty line must start a known diagram type.
    body = re.sub(r"%%\{.*?\}%%", "", text, flags=re.DOTALL).strip()
    assert body.startswith(DIAGRAM_TYPES), f"{name}: no recognised mermaid diagram type"


@pytest.mark.parametrize("name", EXPECTED)
def test_subgraphs_are_balanced(name):
    text = _read(name)
    opens = len(re.findall(r"^\s*subgraph\b", text, flags=re.MULTILINE))
    ends = len(re.findall(r"^\s*end\b", text, flags=re.MULTILINE))
    assert opens == ends, f"{name}: {opens} subgraph vs {ends} end"


def test_capability_ladder_source_has_l0_to_l4_and_eu_classes():
    text = _read("09-capability-tier-ladder")
    for tier in ("L0", "L1", "L2", "L3", "L4"):
        assert tier in text, f"capability-ladder source missing tier {tier}"
    # Seed the Stage 2 gate: every EU risk class from repo.config must appear in the source.
    with open(os.path.join(REPO, "repo.config.json"), encoding="utf-8") as fh:
        cfg = json.load(fh)
    for tier in cfg["capabilityLadder"]:
        assert tier["euRiskClass"] in text, (
            f"capability-ladder source missing EU class '{tier['euRiskClass']}'"
        )
