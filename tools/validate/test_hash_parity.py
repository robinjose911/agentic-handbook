"""Validator: the TS and Python mock-LLM bindings hash a shared corpus to byte-identical digests.

This is the cross-language parity gate. The two bindings hand-implement canonical JSON; this test
pins the contract with a committed corpus so any divergence (a number-format tweak, a key-order
change, a new hashed field touched in only one language) fails here instead of silently splitting the
fixture namespace at runtime.
"""
import json
import os
import shutil
import subprocess

import pytest

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MOCK = os.path.join(REPO, "tools", "mock-llm")

import sys  # noqa: E402

sys.path.insert(0, MOCK)
import mock_llm  # noqa: E402


def _corpus():
    with open(os.path.join(MOCK, "parity-corpus.json"), encoding="utf-8") as fh:
        return json.load(fh)


def test_corpus_is_nonempty_and_varied():
    corpus = _corpus()
    assert len(corpus) >= 5
    # Must exercise unicode + nested objects + numbers, or the gate proves little.
    blob = json.dumps(corpus, ensure_ascii=False)
    assert "café" in blob and "日本語" in blob
    assert "0.7" in blob  # a decimal
    assert "1.0" in blob  # an integer-valued float


def test_python_and_typescript_hash_the_corpus_identically():
    node = shutil.which("node")
    if node is None:
        pytest.skip("node not found — the all.py runner already hard-fails on missing node")
    corpus = _corpus()
    py_hashes = [mock_llm.hash_request(r) for r in corpus]

    result = subprocess.run(
        [node, "--experimental-strip-types", os.path.join(MOCK, "hash_corpus.mjs")],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"node hash_corpus failed:\n{result.stderr}"
    ts_hashes = [ln for ln in result.stdout.strip().splitlines() if ln]

    assert len(ts_hashes) == len(py_hashes), (
        f"corpus length mismatch: {len(ts_hashes)} TS vs {len(py_hashes)} Python"
    )
    for i, (py, ts) in enumerate(zip(py_hashes, ts_hashes)):
        assert py == ts, f"corpus[{i}] hash diverges: python={py} ts={ts}"
