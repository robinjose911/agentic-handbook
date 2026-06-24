# 14 · Observability (lite)

You cannot operate what you cannot see, and an agent is the hardest thing to see in your stack: it
writes its own control flow, calls tools you did not predict, and fails in ways a stack trace never
captures. "Lite" here means the minimum instrumentation that lets a CPTO answer three questions in
production — *what did the agent do, why did it cost that, and is it still as good as it was at
launch?* — without building an observability platform from scratch. The discipline is to emit
structured, standards-aligned events from day one, because retrofitting traces onto a misbehaving
agent during an incident is how you discover what you should have logged.

This chapter is the operational half of the **E** in AGENTIC; [chapter 13](13-evaluations.md) is the
other half. Observability tells you what happened on real traffic; evaluation tells you whether it was
good. They are one loop, and the loop is the point.

![The eval/observability loop](../assets/diagrams/08-eval-observability-loop.png)

## Standardize on OpenTelemetry GenAI conventions

Do not invent a bespoke log format. The
[OpenTelemetry GenAI semantic conventions](../references.md#otel-genai) now define agent-specific
spans and metrics, and adopting them buys you vendor-portability for free: the same instrumentation
flows into [Langfuse](../references.md#langfuse), [Arize Phoenix](../references.md#arize-phoenix), or
any OTel-compatible backend without re-instrumenting. Tool choice is reversible; a homegrown schema is
not.

The model is a tree of **spans**. The conventions give agents a lifecycle vocabulary:

- **`create_agent`** — the span for instantiating an agent, carrying `gen_ai.agent.name` and the
  system instructions/tool definitions it was configured with.
- **`invoke_agent`** — the root span for one agent run (one "task"). Everything the agent does on
  that task hangs underneath it.
- **`execute_tool {tool_name}`** — one tool invocation, carrying `gen_ai.tool.name`, the call id, and
  optionally arguments and result. This is where side effects live, so it is where approval and
  idempotency metadata belong.

Underneath `invoke_agent` you also get the inference spans for each model call, carrying token usage
(`gen_ai.usage.input_tokens` / `gen_ai.usage.output_tokens`, plus cache-read and cache-creation
tokens). The parent/child structure is what lets you reconstruct a full run: a slow task becomes a
flame graph, and you can see at a glance whether the 9-second p95 was the model thinking or a tool
hanging. That distinction changes the fix entirely, and without spans you are guessing.

Two metrics carry most of the operational weight. **Operation duration**
(`gen_ai.client.operation.duration`, a histogram) is your latency SLI; bucket it by operation and
model so a regression in one route does not hide in the aggregate. **Token usage**
(`gen_ai.client.token.usage`) is your cost SLI before it becomes a bill — emit it per call and you can
build cost-per-task by summing over a trace, which is exactly the
[cost-per-task SLO](../templates/agent-slo-definition.md) you committed to. Counting tokens after the
invoice arrives is not observability; it is accounting.

## The payload-by-reference pattern

Agent payloads are large and dangerous to inline. A single run can carry tens of thousands of tokens
of prompt, retrieved context, and tool output, and that content frequently contains PII, secrets, or
customer data. Putting it in your log lines bloats your logging bill, smears sensitive data across an
index built for search rather than for deletion, and makes a retention or right-to-erasure request a
forensic exercise.

The pattern is **payload-by-reference**: the span carries the cheap, queryable metadata (ids,
timings, token counts, status, tool name, the approver) inline, and the heavy, sensitive payload —
the full prompt, the model response, the raw tool arguments — is written to object storage and
referenced by an opaque id. The
[observability event schema](../templates/observability-event-schema.json) encodes this directly: it
requires `event_id`, `trace_id`, `timestamp`, `event_type`, and `status`, but the full content lives
behind a `payload_ref` like `s3://traces/trace_a1/span_2.json`. A representative event:

```json
{
  "event_id": "evt_01HQ7", "trace_id": "trace_a1", "span_id": "span_5",
  "event_type": "tool_call", "agent": { "name": "support-triage", "capability_tier": "L1" },
  "tool": { "name": "issue_refund", "side_effecting": true, "approved_by": "ops:jordan" },
  "status": "ok", "payload_ref": "s3://traces/trace_a1/span_5.json"
}
```

This buys you three things at once. Your trace index stays small and fast, so dashboards and alerts
run on metadata that was never sensitive. Deletion becomes tractable: the reference store has its own
lifecycle policy, and erasing a customer's payloads is a prefix delete, not a re-index. And access
control splits cleanly — most engineers debug from the metadata, while the raw payloads sit behind a
tighter grant, which matters when an
[EU AI Act high-risk system](12-eu-ai-act-as-architecture.md) obliges you to keep automatic logs
(Art. 12) without turning the log store into a second copy of your customer database. Note the
`side_effecting` and `approved_by` fields: that is your audit trail for who authorized a spend or a
send, reconstructable per-decision long after the run.

## The eval ↔ observability loop

Traces and evals are not two systems; they are two phases of one cycle, and the diagram above is the
shape of it. Observability captures real runs. Those runs surface failures — a wrong refund, a
hallucinated citation, an escalation that should not have happened — that no synthetic test
anticipated. You promote those traces into your eval set as new golden cases, so the regression you
just lived through can never ship silently again. Then the next change runs against the enriched eval
set ([chapter 13](13-evaluations.md)) before it reaches production, where observability watches it on
live traffic, and the loop closes.

Concretely, wire it like this. Sample production traces (skewed toward escalations, low-confidence
decisions, and anything a human overrode) and triage them. The clear failures become labeled eval
cases; the ambiguous ones become judge-calibration material. Your drift detector then watches the
production quality signal — groundedness on a sampled fraction, or success rate from a downstream
outcome — and when it falls more than a couple of points against the launch baseline, that is a
[SLO alert](../templates/agent-slo-definition.md), not a quarterly surprise. An agent that is only
evaluated at launch and only observed in aggregate will degrade in ways nobody notices until a
customer does. The loop is what keeps a launched agent honest, and it is the difference between
shipping an agent and operating one.
