"""Deterministic run harness (Python): a synthetic clock (no datetime.now), a tracer emitting events
that conform to templates/observability-event-schema.json, and a stable JSON writer. Determinism is
the point — two runs must produce byte-identical artifacts."""
from __future__ import annotations

import json
from dataclasses import dataclass, field

# Synthetic clock: a fixed date + a time-of-day base advanced by a fixed step per event. Deterministic
# (never datetime.now()). Events stay within the day, so the date is constant 2026-06-24.
_BASE_TOD_MS = 10 * 3_600_000  # 10:00:00.000 within the day
_STEP_MS = 250


def _iso(seq: int) -> str:
    """Valid ISO-8601 (UTC) timestamp for event `seq`: 2026-06-24T10:00:00.000Z + seq*step."""
    ms = _BASE_TOD_MS + seq * _STEP_MS
    hh = ms // 3_600_000
    mm = (ms // 60_000) % 60
    ss = (ms // 1000) % 60
    millis = ms % 1000
    return f"2026-06-24T{hh:02d}:{mm:02d}:{ss:02d}.{millis:03d}Z"


@dataclass
class Tracer:
    trace_id: str
    agent: dict
    events: list = field(default_factory=list)
    _seq: int = 0

    def emit(self, event_type: str, status: str, attributes: dict | None = None) -> dict:
        seq = self._seq
        self._seq += 1
        ev = {
            "event_id": f"{self.trace_id}-{seq}",
            "trace_id": self.trace_id,
            "span_id": f"span-{seq}",
            "timestamp": _iso(seq),
            "event_type": event_type,
            "agent": self.agent,
            "status": status,
            "duration_ms": _STEP_MS,
        }
        if attributes:
            ev["attributes"] = attributes
        self.events.append(ev)
        return ev

    def to_jsonl(self) -> str:
        return "".join(json.dumps(e, sort_keys=True) + "\n" for e in self.events)


def stable_json(obj) -> str:
    """Sorted-key, 2-space JSON with a trailing newline — byte-stable across machines."""
    return json.dumps(obj, sort_keys=True, indent=2) + "\n"
