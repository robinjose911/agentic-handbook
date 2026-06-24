"""Validator: the 16 procurement templates conform to the uniform format + their specific
requirements (Stage 2.1)."""
import json
import os
import re

import jsonschema
import pytest

from catalog import TEMPLATES_MD as MARKDOWN_TEMPLATES, TEMPLATES_JSON as JSON_TEMPLATES  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TPL = os.path.join(REPO, "templates")

ALL_TEMPLATES = MARKDOWN_TEMPLATES + JSON_TEMPLATES  # 16 total

REQUIRED_HEADER_FIELDS = ["**Purpose:**", "**When to use:**", "**How to fill:**"]


def _read_md(name: str) -> str:
    with open(os.path.join(TPL, f"{name}.md"), encoding="utf-8") as fh:
        return fh.read()


def test_there_are_sixteen_templates():
    assert len(ALL_TEMPLATES) == 16


@pytest.mark.parametrize("name", MARKDOWN_TEMPLATES + ["README"])
def test_markdown_file_exists(name):
    assert os.path.exists(os.path.join(TPL, f"{name}.md")), f"missing templates/{name}.md"


@pytest.mark.parametrize("name", MARKDOWN_TEMPLATES)
def test_markdown_template_has_uniform_header_and_body(name):
    text = _read_md(name)
    assert text.lstrip().startswith("# "), f"{name}: must open with an H1 title"
    for field in REQUIRED_HEADER_FIELDS:
        assert field in text, f"{name}: missing header field {field}"
    assert re.search(r"^##\s+\S", text, flags=re.MULTILINE), f"{name}: needs at least one body H2"


def test_templates_index_lists_all_sixteen():
    idx = _read_md("README")
    for name in ALL_TEMPLATES:
        assert name in idx, f"templates/README.md does not list {name}"


def test_agent_vendor_rfp_has_at_least_30_numbered_questions():
    text = _read_md("agent-vendor-rfp")
    # Count numbered questions like "1." ... "37." at line start.
    numbered = re.findall(r"^\s*\d+\.\s+\S", text, flags=re.MULTILINE)
    assert len(numbered) >= 30, f"agent-vendor-rfp has {len(numbered)} numbered questions, need >=30"


def test_production_readiness_has_all_go_no_go_gates():
    # Each gate must be an actual `## ` section, not just a word appearing somewhere in the file —
    # otherwise deleting a whole gate section passes as long as the word survives in another bullet.
    text = _read_md("production-readiness-checklist")
    headings = " | ".join(l.lower() for l in text.splitlines() if l.startswith("## "))
    for gate in ["security", "privacy", "cost", "reliability", "rollback",
                 "monitoring", "eval", "incident", "eu ai act"]:
        assert gate in headings, f"production-readiness-checklist has no '## ' gate section for: {gate}"


def test_template_directory_has_no_orphans():
    # Pin the directory: every *.md / *.json in templates/ must be a registered, validated template
    # (or the README). A stray draft would otherwise ship unvalidated and unindexed.
    md = {f[:-3] for f in os.listdir(TPL) if f.endswith(".md")}
    expected_md = set(MARKDOWN_TEMPLATES) | {"README"}
    assert md == expected_md, f"unexpected/missing templates/*.md: {md ^ expected_md}"
    js = {f[:-5] for f in os.listdir(TPL) if f.endswith(".json")}
    assert js == set(JSON_TEMPLATES), f"unexpected/missing templates/*.json: {js ^ set(JSON_TEMPLATES)}"


def test_prompt_injection_threat_model_enumerates_exposures():
    text = _read_md("prompt-injection-threat-model").lower()
    assert "direct" in text and "indirect" in text, "must cover direct + indirect injection"
    assert "lethal trifecta" in text, "must cover the lethal trifecta exposure"


def test_observability_event_schema_is_valid_and_round_trips():
    with open(os.path.join(TPL, "observability-event-schema.json"), encoding="utf-8") as fh:
        schema = json.load(fh)
    # It must be a valid JSON Schema (the metaschema check raises on a broken schema).
    Validator = jsonschema.validators.validator_for(schema)
    Validator.check_schema(schema)
    validator = Validator(schema)
    examples = schema.get("examples", [])
    assert examples, "schema must ship at least one example event to round-trip"
    for i, ex in enumerate(examples):
        errors = list(validator.iter_errors(ex))
        assert not errors, f"example[{i}] fails its own schema: {[e.message for e in errors]}"
