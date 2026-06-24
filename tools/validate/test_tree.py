"""Validator: the repo skeleton, repo.config.json, and git-ignore rules are correct (Stage 0.1 + 0.2)."""
import json
import os
import subprocess

import pytest

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

REQUIRED_PATHS = [
    "README.md", "LICENSE", "CONTRIBUTING.md", "SECURITY.md",
    "AGENTS.md", "llms.txt", "references.md", "repo.config.json",
    "CLAUDE.md", ".gitignore",
    ".github/workflows", ".github/ISSUE_TEMPLATE", ".github/instructions",
    "docs", "templates", "presentations/src",
    "assets/diagrams/src", "assets/images", "assets/manifest.json",
    "examples/typescript", "examples/python",
    "tools/preview", "tools/validate", "tools/stubs", "tools/links",
    "tools/mock-llm", "tools/presentations", "tools/requirements.txt",
    "tests/e2e",
]


@pytest.mark.parametrize("rel", REQUIRED_PATHS)
def test_required_path_exists(rel):
    assert os.path.exists(os.path.join(REPO, rel)), f"missing required path: {rel}"


def test_repo_config_parses_with_required_keys():
    with open(os.path.join(REPO, "repo.config.json"), encoding="utf-8") as fh:
        cfg = json.load(fh)
    for key in ["owner", "repoName", "theme", "tagline", "definition", "mnemonic",
                "capabilityLadder", "badges", "buttons", "socialPreviewText", "accuracyStance"]:
        assert key in cfg, f"repo.config.json missing key: {key}"
    assert cfg["repoName"] == "agentic-handbook"


def test_mnemonic_spells_agentic_with_seven_surfaces():
    with open(os.path.join(REPO, "repo.config.json"), encoding="utf-8") as fh:
        cfg = json.load(fh)
    surfaces = cfg["mnemonic"]["surfaces"]
    assert len(surfaces) == 7, "AGENTIC must have exactly 7 surfaces"
    assert "".join(s["letter"] for s in surfaces) == "AGENTIC"
    names = [s["name"] for s in surfaces]
    assert names == ["Autonomy", "Goals", "Evaluation", "Networks", "Trust", "Identity", "Cost"]
    for s in surfaces:
        assert s["chapters"], f"surface {s['letter']} maps to no chapters"


def test_capability_ladder_has_l0_to_l4():
    with open(os.path.join(REPO, "repo.config.json"), encoding="utf-8") as fh:
        cfg = json.load(fh)
    tiers = [t["tier"] for t in cfg["capabilityLadder"]]
    assert tiers == ["L0", "L1", "L2", "L3", "L4"]


def _check_ignored(rel: str) -> bool:
    result = subprocess.run(
        ["git", "check-ignore", rel], cwd=REPO, capture_output=True, text=True
    )
    return result.returncode == 0


def test_samples_and_claude_md_are_git_ignored():
    assert _check_ignored("samples/"), "samples/ must be git-ignored"
    assert _check_ignored("CLAUDE.md"), "CLAUDE.md must be git-ignored"
    assert _check_ignored(".claude/"), ".claude/ must be git-ignored"


def test_claude_md_has_required_sections():
    with open(os.path.join(REPO, "CLAUDE.md"), encoding="utf-8") as fh:
        text = fh.read()
    for heading in ["What this repo is", "Build conventions", "Where the tooling lives",
                    "How to run the tests"]:
        assert heading in text, f"CLAUDE.md missing section: {heading}"
