"""Deterministic run harness (Python edition of 01's harness.ts).

A synthetic clock (no datetime.now()), a Tracer that emits events conforming to
templates/observability-event-schema.json, and stable-JSON writers. Determinism is the whole point:
two runs must produce byte-identical trace.jsonl + eval-report.json + receipt.json.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# Fixed base instant; each event advances it by a fixed step so timestamps are deterministic.
# Mirrors harness.ts: Date.parse("2026-06-24T10:00:00.000Z") + seq * 250ms, rendered with millis + Z.
_BASE_MS = 1782295200000  # 2026-06-24T10:00:00.000Z, in epoch milliseconds
_STEP_MS = 250

_EVENT_TYPES = {"agent_step", "llm_call", "tool_call", "decision", "approval", "escalation", "error"}
_STATUSES = {"ok", "error", "escalated", "rejected"}


def _iso(ms: int) -> str:
    """Render an epoch-millisecond instant as 'YYYY-MM-DDTHH:MM:SS.mmmZ' (matches JS toISOString)."""
    secs, millis = divmod(ms, 1000)
    days, rem = divmod(secs, 86400)
    hh, rem = divmod(rem, 3600)
    mm, ss = divmod(rem, 60)
    # 2026-06-24 is day 20629 since the Unix epoch; _BASE_MS lands exactly at 10:00:00 on that date,
    # and every step keeps us inside the same UTC day, so a fixed date prefix is correct and stable.
    base_days = 20628  # days from 1970-01-01 to 2026-06-24
    assert days == base_days, "synthetic clock walked off 2026-06-24 — widen the date logic"
    return f"2026-06-24T{hh:02d}:{mm:02d}:{ss:02d}.{millis:03d}Z"


@dataclass
class Tracer:
    """Emits OTel-GenAI-shaped lifecycle events with a synthetic monotonic clock."""

    trace_id: str
    agent: Dict[str, str]
    events: List[Dict[str, Any]] = field(default_factory=list)
    _seq: int = 0

    def emit(
        self,
        event_type: str,
        status: str,
        attributes: Optional[Dict[str, Any]] = None,
        tokens: Optional[Dict[str, int]] = None,
    ) -> Dict[str, Any]:
        assert event_type in _EVENT_TYPES, f"bad event_type {event_type!r}"
        assert status in _STATUSES, f"bad status {status!r}"
        seq = self._seq
        self._seq += 1
        ev: Dict[str, Any] = {
            "event_id": f"{self.trace_id}-{seq}",
            "trace_id": self.trace_id,
            "span_id": f"span-{seq}",
            "timestamp": _iso(_BASE_MS + seq * _STEP_MS),
            "event_type": event_type,
            "agent": self.agent,
            "status": status,
            "duration_ms": _STEP_MS,
        }
        if tokens is not None:
            ev["tokens"] = tokens
        if attributes is not None:
            ev["attributes"] = attributes
        self.events.append(ev)
        return ev

    def to_jsonl(self) -> str:
        # One compact JSON object per line; sorted keys so committed bytes are stable.
        return "".join(json.dumps(e, sort_keys=True, separators=(",", ":")) + "\n" for e in self.events)


def stable_json(value: Any) -> str:
    """Stable JSON (sorted keys, 2-space indent, trailing newline) so artifacts are byte-stable."""
    return json.dumps(value, sort_keys=True, indent=2) + "\n"
