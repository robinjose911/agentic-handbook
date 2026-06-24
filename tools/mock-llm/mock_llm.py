"""Deterministic mock LLM provider (Python binding).

`complete(request)` hashes the canonical `(system, messages, tools)` of the request and returns the
canned response recorded under a `fixtures/` directory. An unrecorded hash raises `MissingFixture`
so a drifting prompt fails loudly instead of silently hitting a real API. No network, no API key.

The hash is computed over a canonical JSON form shared byte-for-byte with the TypeScript binding
(`index.ts`), so a single `fixtures/<hash>.json` works for both languages.

Recording (off in CI): call `record(request, response, fixtures_dir)` to author a fixture. There is
no real-provider call here — this scaffold is offline by construction.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from typing import Any, Dict

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_FIXTURES = os.path.join(HERE, "fixtures")


class MissingFixture(KeyError):
    """Raised when no recorded fixture matches the request hash."""


# Numbers must be finite and within the range where JS and Python serialize identically. Above
# 2**53 JS loses integer precision and switches to exponential notation (1e+21), and non-finite
# values disagree (Python "NaN"/"Infinity" vs JS "null"). Both bindings reject the same out-of-range
# numbers, so a request either hashes identically in both languages or fails loudly in both — never a
# silent cross-language hash split. LLM request payloads (token counts, temperatures, schema bounds)
# are always well inside this range, so the guard never trips in practice.
_MAX_SAFE = 2 ** 53


def _normalize(value: Any) -> Any:
    """Collapse integer-valued floats to int (so 1.0 serializes as "1", matching JS) and reject any
    number outside the cross-language-safe range."""
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        if abs(value) >= _MAX_SAFE:
            raise ValueError(f"integer {value} is outside the canonicalizable range (|n| < 2**53)")
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"non-finite number {value!r} cannot be canonicalized")
        if abs(value) >= _MAX_SAFE:
            raise ValueError(f"number {value!r} is outside the canonicalizable range (|n| < 2**53)")
        return int(value) if value.is_integer() else value
    if isinstance(value, dict):
        return {k: _normalize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_normalize(v) for v in value]
    return value


def _canonical(obj: Any) -> str:
    """Canonical JSON shared byte-for-byte with index.ts: sorted keys, no spaces, raw unicode,
    integer-valued floats normalized."""
    return json.dumps(_normalize(obj), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _canonical_request(request: Dict[str, Any]) -> str:
    """Canonical JSON of only the hash-relevant fields. Must match index.ts exactly."""
    keyed = {
        "system": request.get("system", ""),
        "messages": request.get("messages", []),
        "tools": request.get("tools", []),
    }
    return _canonical(keyed)


def hash_request(request: Dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_request(request).encode("utf-8")).hexdigest()


class MockProvider:
    def __init__(self, fixtures_dir: str = DEFAULT_FIXTURES):
        self.fixtures_dir = fixtures_dir

    def complete(self, request: Dict[str, Any]) -> Dict[str, Any]:
        digest = hash_request(request)
        path = os.path.join(self.fixtures_dir, f"{digest}.json")
        if not os.path.exists(path):
            raise MissingFixture(
                f"no fixture for request hash {digest} in {self.fixtures_dir}. "
                f"The prompt may have drifted; re-record the fixture."
            )
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)["response"]


def record(request: Dict[str, Any], response: Dict[str, Any], fixtures_dir: str = DEFAULT_FIXTURES) -> str:
    """Write a fixture for `request` -> `response`. Returns the fixture path. Deterministic."""
    os.makedirs(fixtures_dir, exist_ok=True)
    digest = hash_request(request)
    path = os.path.join(fixtures_dir, f"{digest}.json")
    # Write the canonical form so a fixture re-recorded by either binding is byte-identical.
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(_canonical({"request": request, "response": response}))
    return path
