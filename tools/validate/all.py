#!/usr/bin/env python3
"""Run every unit validator and exit non-zero on any failure.

Runs the Python validators (pytest over a target dir, default `tools/validate`) plus the Node
unit tests (the preview render harness and the mock-LLM TS binding). The Node checks can be skipped
with `--no-node` (used by the runner's own self-test to avoid spawning Node).

Usage:
    python tools/validate/all.py [--target DIR] [--no-node]
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))


def discover_validators(target: str) -> list[str]:
    """Return the sorted list of `test_*.py` validator files under `target`."""
    found: list[str] = []
    for root, _dirs, files in os.walk(target):
        for f in files:
            if f.startswith("test_") and f.endswith(".py"):
                found.append(os.path.join(root, f))
    return sorted(found)


def run_pytest(target: str) -> int:
    print(f"== pytest {os.path.relpath(target, REPO)} ==", flush=True)
    rc = subprocess.call([sys.executable, "-m", "pytest", "-q", target])
    if rc == 5:  # pytest exit 5 = "no tests collected" — an empty target is not a failure
        print("   (no tests collected)", flush=True)
        return 0
    return rc


def run_node_checks() -> list[tuple[str, int]]:
    checks = [
        ("preview render harness", ["node", os.path.join(REPO, "tools", "preview", "test_build.mjs")]),
        (
            "mock-llm TS binding",
            ["node", "--experimental-strip-types", os.path.join(REPO, "tools", "mock-llm", "index.test.ts")],
        ),
        (
            "url-classifier",
            ["node", "--experimental-strip-types",
             os.path.join(REPO, "tests", "e2e", "helpers", "urls.selftest.mjs")],
        ),
    ]
    results: list[tuple[str, int]] = []
    for name, cmd in checks:
        print(f"== node: {name} ==", flush=True)
        try:
            rc = subprocess.call(cmd)
        except FileNotFoundError:
            # Node is required for these checks; a missing binary is a hard failure, not a silent pass.
            print(f"   ERROR ({name}): node not found on PATH — required for the preview + mock-llm "
                  f"checks. Install Node 22+ or run with --no-node to skip explicitly.", flush=True)
            rc = 1
        results.append((name, rc))
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=os.path.join(HERE), help="dir of validators to run")
    parser.add_argument("--no-node", action="store_true", help="skip the Node unit checks")
    args = parser.parse_args(argv)

    failures: list[str] = []

    validators = discover_validators(args.target)
    print(f"discovered {len(validators)} validator file(s)", flush=True)

    if validators:
        if run_pytest(args.target) != 0:
            failures.append("pytest")
    else:
        print("no validators discovered — skipping pytest", flush=True)

    if not args.no_node:
        for name, rc in run_node_checks():
            if rc != 0:
                failures.append(f"node:{name}")

    if failures:
        print(f"\nFAILED: {', '.join(failures)}", flush=True)
        return 1
    print("\nall validators passed", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
