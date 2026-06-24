"""Validator (shared, Stage 5): every runnable example has the required files, re-runs deterministically
(byte-identical artifacts), its trace conforms to the observability schema, its README's headline numbers
equal its receipt, and its safety/gate invariant holds."""
import json
import os
import re
import subprocess
import sys
from datetime import datetime

import jsonschema
import pytest

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCHEMA_PATH = os.path.join(REPO, "templates", "observability-event-schema.json")

TS_RUN = ["node", "--experimental-strip-types", "run.ts"]
PY_RUN = [sys.executable, "run.py"]

# Each example: dir, the command that produces the receipts, and any EXTRA committed artifacts that must
# also be byte-stable (05's EU AI Act Art. 11/12 compliance evidence).
EXAMPLES = [
    {"path": "examples/typescript/01-support-triage-agent", "run": TS_RUN, "lang": "ts"},
    {"path": "examples/typescript/02-outbound-lead-workflow-agent", "run": TS_RUN, "lang": "ts"},
    {"path": "examples/typescript/03-evaluator-optimizer-self-improving", "run": TS_RUN, "lang": "ts"},
    {"path": "examples/python/04-research-synthesis-multi-agent", "run": PY_RUN, "lang": "py"},
    {
        "path": "examples/python/05-healthcare-intake-regulated-domain",
        "run": PY_RUN,
        "lang": "py",
        "extra": ["audit-log.jsonl", "technical-doc.json"],
    },
]

ARTIFACTS = ["trace.jsonl", "eval-report.json", "receipt.json"]
REQUIRED = ["README.md", "eval", "fixtures"] + ARTIFACTS
_MISSING_DEP = ("Cannot find module", "ERR_MODULE_NOT_FOUND", "ModuleNotFoundError", "No module named")


# Per-example safety / gate invariants over (receipt, eval_report). Each must be EARNED, not asserted.
def _inv_01(r, _rep):
    return r.get("gatePassed") is True and r["classificationPassRate"] >= r["gate"]


def _inv_02(r, _rep):
    return r.get("budgetHonored") is True and r["maxLeadCostUsd"] <= r["costCapUsd"]


def _inv_03(r, _rep):
    climb = r.get("scoreClimb") or r.get("headline", {}).get("scoreClimb", "")
    scores = [float(x) for x in re.findall(r"[0-9]*\.?[0-9]+", climb)]
    non_decreasing = all(b >= a for a, b in zip(scores, scores[1:]))
    net_improvement = len(scores) >= 2 and scores[-1] > scores[0]  # a real climb, not a flat line
    return (
        r.get("gatePassed") is True
        and float(r["finalScore"]) >= float(r["gate"])
        and non_decreasing
        and net_improvement
        and scores[-1] == float(r["finalScore"])
    )


def _inv_04(r, _rep):
    return r.get("gatePassed") is True and r["groundednessScore"] >= float(r.get("gate", 1.0))


def _inv_05(r, _rep):
    return (
        r.get("safetyAllPass") is True
        and r.get("noSilentAutoHandle") is True
        and r["mustEscalateMade"] == r["mustEscalateTotal"]
        and r["failSafeCases"] >= 1  # the fail-safe (unknown/unparseable) branch is actually exercised
    )


INVARIANTS = {
    "01-support-triage-agent": _inv_01,
    "02-outbound-lead-workflow-agent": _inv_02,
    "03-evaluator-optimizer-self-improving": _inv_03,
    "04-research-synthesis-multi-agent": _inv_04,
    "05-healthcare-intake-regulated-domain": _inv_05,
}


def _ids(ex):
    return ex["path"].split("/")[-1]


def _artifacts(ex):
    return ARTIFACTS + ex.get("extra", [])


@pytest.mark.parametrize("ex", EXAMPLES, ids=_ids)
def test_required_files_exist(ex):
    base = os.path.join(REPO, ex["path"])
    entry = "run.ts" if ex["lang"] == "ts" else "run.py"
    for rel in REQUIRED + [entry]:
        assert os.path.exists(os.path.join(base, rel)), f"{ex['path']}: missing {rel}"


@pytest.mark.parametrize("ex", EXAMPLES, ids=_ids)
def test_receipt_headline_matches_readme(ex):
    base = os.path.join(REPO, ex["path"])
    receipt = json.load(open(os.path.join(base, "receipt.json"), encoding="utf-8"))
    assert receipt.get("headline"), f"{ex['path']}: receipt has no headline block"
    readme = open(os.path.join(base, "README.md"), encoding="utf-8").read()
    for key, value in receipt["headline"].items():
        token = re.escape(str(value))
        # Word-boundary-ish match: the value must not be embedded in a larger number (so 7 != 17/70).
        assert re.search(rf"(?<![\w.]){token}(?![\w.])", readme), (
            f"{ex['path']}: headline {key}={value!r} not found as a standalone token in README "
            f"(prose-vs-receipt drift)"
        )


@pytest.mark.parametrize("ex", EXAMPLES, ids=_ids)
def test_trace_events_conform_to_schema(ex):
    with open(SCHEMA_PATH, encoding="utf-8") as fh:
        schema = json.load(fh)
    validator_cls = jsonschema.validators.validator_for(schema)
    validator_cls.check_schema(schema)
    validator = validator_cls(schema)
    base = os.path.join(REPO, ex["path"])
    with open(os.path.join(base, "trace.jsonl"), encoding="utf-8") as fh:
        lines = [ln for ln in fh.read().splitlines() if ln.strip()]
    assert lines, f"{ex['path']}: trace.jsonl is empty"
    for i, line in enumerate(lines):
        ev = json.loads(line)
        errors = [e.message for e in validator.iter_errors(ev)]
        assert not errors, f"{ex['path']} trace[{i}] fails schema: {errors}"
        # Format checkers may be skipped without the optional extra, so parse the timestamp explicitly.
        datetime.fromisoformat(ev["timestamp"].replace("Z", "+00:00"))


@pytest.mark.parametrize("ex", EXAMPLES, ids=_ids)
def test_run_is_deterministic_and_receipts_current(ex):
    base = os.path.join(REPO, ex["path"])
    arts = _artifacts(ex)
    saved = {a: open(os.path.join(base, a), "rb").read() for a in arts}
    try:
        result = subprocess.run(ex["run"], cwd=base, capture_output=True, text=True, timeout=180)
    except FileNotFoundError:
        pytest.skip(f"{ex['run'][0]} not found")
    if result.returncode != 0:
        if any(m in (result.stderr or "") for m in _MISSING_DEP):
            pytest.skip(f"{ex['path']}: deps not installed")
        raise AssertionError(f"{ex['path']} run failed:\n{result.stderr}")
    drifted = []
    for a in arts:
        now = open(os.path.join(base, a), "rb").read()
        if now != saved[a]:
            drifted.append(a)
            with open(os.path.join(base, a), "wb") as fh:  # restore committed bytes
                fh.write(saved[a])
    assert not drifted, (
        f"{ex['path']}: re-running changed {drifted} — non-deterministic or stale committed artifacts."
    )


@pytest.mark.parametrize("ex", EXAMPLES, ids=_ids)
def test_receipt_invariant_holds(ex):
    base = os.path.join(REPO, ex["path"])
    receipt = json.load(open(os.path.join(base, "receipt.json"), encoding="utf-8"))
    report = json.load(open(os.path.join(base, "eval-report.json"), encoding="utf-8"))
    assert INVARIANTS[_ids(ex)](receipt, report), (
        f"{ex['path']}: receipt safety/gate invariant failed: {receipt}"
    )


@pytest.mark.parametrize("ex", EXAMPLES, ids=_ids)
def test_receipt_agrees_with_eval_report(ex):
    base = os.path.join(REPO, ex["path"])
    receipt = json.load(open(os.path.join(base, "receipt.json"), encoding="utf-8"))
    report = json.load(open(os.path.join(base, "eval-report.json"), encoding="utf-8"))
    for key in ("passed", "total", "passRate", "gate", "mustEscalateMade", "groundednessScore"):
        if key in receipt and key in report:
            assert receipt[key] == report[key], f"{ex['path']}: receipt.{key} != eval-report.{key}"
