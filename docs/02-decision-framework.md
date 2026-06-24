# 02 · Decision framework

The most valuable decision in agent engineering is **not building one**. This chapter is the decision
tree: when a plain function beats an LLM, when a workflow beats an agent, and when multi-agent beats a
single agent. The hero diagram is the artifact — copy it into your design review.

![The agent-vs-workflow decision tree](../assets/diagrams/00-hero-decision-tree.png)

## Step 1 — Do you need a model at all?

If the task has a deterministic, enumerable set of steps, write code. An LLM adds latency, cost, and a
new failure surface; spend them only where you need a model's judgement over fuzzy input. "We could
use AI here" is not a reason; "no rule expresses this judgement" is.

## Step 2 — Workflow or agent?

This is the load-bearing distinction, and the industry has converged on it. A **workflow** is a system
where *you* wire the path between LLM calls in code — predictable, inspectable, cheap to test. An
**agent** is a system where the *model* directs its own control flow and tool use, deciding when it is
done ([Anthropic, "Building Effective Agents"](../references.md#anthropic-building-effective-agents)).

The guidance is blunt: **prefer the workflow.** Reach for an agent only when the task genuinely needs
a dynamic, model-chosen path — when you cannot enumerate the steps in advance because they depend on
what the agent discovers along the way. Most production value is captured by workflows; agents are a
power tool with a recoil.

## Step 3 — Single agent or multi-agent?

Here the field had a public argument, and the resolution is now usable:

- [Cognition, "Don't Build Multi-Agents"](../references.md#cognition-dont-build-multi-agents) (June
  2025) argues that splitting work across agents fractures context and produces incoherent results for
  **tightly-dependent** tasks — the sub-agents make conflicting assumptions.
- [Anthropic's multi-agent research system](../references.md#anthropic-multi-agent-research) (June
  2025) shows multi-agent winning for **breadth-first, parallelizable** research where sub-tasks are
  weakly coupled.
- [Cognition's April 2026 follow-up](../references.md#cognition-multi-agents-working) reconciles them:
  **single-agent for deep, dependent work; multi-agent for breadth-first work with weak inter-task
  dependencies.**

The reason to be conservative is empirical. The [Berkeley MAST taxonomy](../references.md#mast-taxonomy)
catalogues 14 multi-agent failure modes across ~1,600 traces (NeurIPS 2025), and they are
**architectural** — specification gaps, inter-agent misalignment, verification gaps — not things a
better prompt fixes (_self-reported; see the paper, verify before relying_). Adding agents adds
coordination failure surface; add them only when the parallelism pays for it.

## The decision, in order

1. **Deterministic steps?** → Write code. No LLM.
2. **One judgement over fuzzy input?** → One LLM call with a structured output.
3. **Several known steps?** → A **workflow** (chain / route / parallelize).
4. **Path must be chosen at runtime by the model?** → A **single agent**, inside hard limits.
5. **Breadth-first, parallelizable, weakly-coupled sub-tasks?** → **Multi-agent**, with explicit
   artifact handoff.
6. **Anything that sets its own cross-domain goals?** → Stop. That is the prohibited tier
   ([capability ladder](../templates/capability-tier-ladder.md)).

## Carrying the decision forward

Whatever rung you land on, record it in an [agent design spec](../templates/agent-design-spec.md) and
a [capability tier](../templates/capability-tier-ladder.md). The tier sets your autonomy rails
([chapter 01](01-mnemonic-and-systems-map.md)), your human-in-the-loop policy, and — because tier
maps to EU AI Act risk class — your compliance posture ([chapter 12](12-eu-ai-act-as-architecture.md)).
The [pattern catalog](03-pattern-catalog.md) gives the concrete shapes for whichever rung you chose.
