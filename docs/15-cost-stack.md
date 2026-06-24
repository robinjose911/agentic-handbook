# 15 · Cost stack

An agent that works but costs more than it saves is a failed agent. This is the **C** (Cost) surface:
three layers of savings, applied in order, plus the model-selection lever from
[chapter 09](09-model-selection-for-roles.md). Every figure here is labeled — cost numbers move with
every pricing change.

## Apply the three layers in order

Cheapest wins first. Do not reach for a router before you have turned on caching.

### 1. Prompt caching

Reuse the expensive, stable prefix of your prompt (system instructions, tool definitions, few-shot
examples) across calls. All figures here are _self-reported, as of June 2026 — verify before
relying_. Anthropic's explicit `cache_control` advertises up to ~90% (self-reported) savings on cached
input; OpenAI's automatic caching ~50% (self-reported); Gemini offers implicit caching. This is the
highest-leverage, lowest-effort lever: a config change, not an architecture change.

### 2. Semantic caching

Cache *answers* keyed by meaning, not exact string — so near-duplicate queries skip the model
entirely. Useful for high-repeat workloads (FAQs, classification). The trade-off is correctness: a
too-loose similarity threshold returns a stale or wrong cached answer, so semantic caching needs its
own eval ([chapter 13](13-evaluations.md)).

### 3. Model routing & cascades

Send easy requests to a cheap model and escalate only the hard ones. [RouteLLM](../references.md#routellm)
reports up to ~85% cost reduction at ~95% of full quality on benchmark workloads (_self-reported — as
of June 2026, verify before relying_). Routing is also a quality lever: it lets a strong orchestrator
spend its budget where it matters ([chapter 09](09-model-selection-for-roles.md)). Batch APIs add a
further discount (~50% off for sub-24h-latency work — _self-reported, verify_).

## The stack, with the math

The layers compound. The table below is a worked, **illustrative** example normalized to a $1.00
baseline per layer — the savings column is recomputed by this repo's validator from the base and
effective cost, so the prose can never drift from its own arithmetic:

| Layer | Base cost | Effective cost | Savings | Note |
|-------|-----------|----------------|---------|------|
| Prompt caching (reuse the stable prefix) | $1.00 | $0.10 | 90% | _illustrative — verify_ |
| Semantic caching (dedupe near-repeat queries) | $1.00 | $0.50 | 50% | _illustrative — verify_ |
| Model routing / cascade (cheap model first) | $1.00 | $0.15 | 85% | _illustrative — verify_ |

These are per-layer illustrations, not a promise; your numbers depend on cache-hit rate, query
repetition, and routing accuracy. Measure them against your own traffic.

## Cost is a reliability control, too

The cheapest token is the one you never spend on a runaway loop. The pre-execution **budget cap** from
[chapter 05](05-memory-state-and-durable-execution.md) — a hard USD/token/step limit enforced *before*
each step — is both a cost lever and a safety control. The $47,000 (illustrative — verify) multi-agent
loop in [chapter 11](11-security-and-threat-model.md) happened because the budget lived on a dashboard
instead of in the loop. Put cost-per-task in your
[SLOs](../templates/agent-slo-definition.md) and your [ROI model](../templates/roi-framework.md), and
treat a cost-cap breach as an incident, not a line item.
