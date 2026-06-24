"""Record step (OFF in CI). Authors the canned mock-provider fixtures from the golden set so the
example runs offline. Re-run only when the prompt or golden inputs change:

    .venv/bin/python record_fixtures.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "mock-llm"))
sys.path.insert(0, HERE)

import mock_llm  # noqa: E402
from src.agent import classify_request  # noqa: E402

with open(os.path.join(HERE, "eval", "golden.json"), encoding="utf-8") as fh:
    golden = json.load(fh)

fixtures_dir = os.path.join(HERE, "fixtures")
n = 0
for g in golden:
    req = classify_request(g["message"])
    # Fail-safe cases carry a raw `cannedContent` (an unknown intent, or non-JSON); others get the
    # well-formed labelled classification.
    content = g.get("cannedContent", json.dumps({"intent": g["expectedIntent"], "reason_code": g["reasonCode"]}))
    resp = {"content": content, "stop_reason": "end_turn", "usage": {"input_tokens": 30, "output_tokens": 8}}
    mock_llm.record(req, resp, fixtures_dir)
    n += 1
print(f"recorded {n} fixtures into fixtures/")
