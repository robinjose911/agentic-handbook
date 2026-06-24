// Deterministic run harness: a synthetic clock (no Date.now), a tracer that emits events conforming
// to templates/observability-event-schema.json, and JSON writers. Determinism is the whole point —
// two runs must produce byte-identical trace.jsonl + eval-report.json + receipt.json.

export interface TraceEvent {
  event_id: string;
  trace_id: string;
  span_id: string;
  timestamp: string;
  event_type: "agent_step" | "llm_call" | "tool_call" | "decision" | "approval" | "escalation" | "error";
  agent: { name: string; capability_tier: string };
  status: "ok" | "error" | "escalated" | "rejected";
  duration_ms: number;
  attributes?: Record<string, unknown>;
}

// Fixed base instant; each event advances it by a fixed step so timestamps are deterministic.
const BASE_MS = Date.parse("2026-06-24T10:00:00.000Z");
const STEP_MS = 250;

export class Tracer {
  events: TraceEvent[] = [];
  traceId: string;
  agent: { name: string; capability_tier: string };
  private seq = 0;
  // No TS parameter properties — the examples run under `node --experimental-strip-types` (erasable-only).
  constructor(traceId: string, agent: { name: string; capability_tier: string }) {
    this.traceId = traceId;
    this.agent = agent;
  }

  emit(
    type: TraceEvent["event_type"],
    status: TraceEvent["status"],
    attributes?: Record<string, unknown>,
  ): TraceEvent {
    const seq = this.seq++;
    const ev: TraceEvent = {
      event_id: `${this.traceId}-${seq}`,
      trace_id: this.traceId,
      span_id: `span-${seq}`,
      timestamp: new Date(BASE_MS + seq * STEP_MS).toISOString(),
      event_type: type,
      agent: this.agent,
      status,
      duration_ms: STEP_MS,
      ...(attributes ? { attributes } : {}),
    };
    this.events.push(ev);
    return ev;
  }

  toJsonl(): string {
    return this.events.map((e) => JSON.stringify(e)).join("\n") + "\n";
  }
}

// Stable JSON (sorted keys) so committed artifacts are byte-stable across machines.
export function stableStringify(value: unknown): string {
  return JSON.stringify(sortKeys(value), null, 2) + "\n";
}

function sortKeys(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(sortKeys);
  if (value && typeof value === "object") {
    const out: Record<string, unknown> = {};
    for (const k of Object.keys(value as Record<string, unknown>).sort()) {
      out[k] = sortKeys((value as Record<string, unknown>)[k]);
    }
    return out;
  }
  return value;
}
