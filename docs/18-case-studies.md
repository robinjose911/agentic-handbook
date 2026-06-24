# 18 · Case studies

> **Sanitized — illustrative figures.** Both case studies below are fictionalized composites built on
> toy datasets. The organizations (Nexora, AIGist24) are synthetic, the architectures are
> representative rather than literal, and every number is marked _illustrative — sanitized; verify
> nothing here as a benchmark_. They exist to show how the patterns in this handbook compose under
> real constraints, not to report results. Do not cite any figure here as evidence of anything.

The chapters in this handbook argue patterns in the abstract. These two studies show the patterns
colliding with reality — where a clean diagram met a per-task budget, a compliance obligation, and a
model that occasionally makes things up. Each follows the same shape: the **situation**, the
**architecture decisions** that mattered, **what we'd build today** with the benefit of hindsight, and
**what we'd avoid**. The second column — hindsight — is the valuable one. Anyone can draw the
architecture that shipped; the lesson is in what the team would change.

## Case study 1 — Nexora outbound calling agent (TypeScript)

### Situation

Nexora ran an outbound calling operation: an agent places a call, works through a goal (confirm an
appointment, collect a missing detail, offer a renewal), and either completes the task or hands off to
a human. The hard constraints were unforgiving. A call is a long-lived, stateful interaction that can
span minutes and must survive a process restart without re-dialing the customer. Every turn costs
money, so a looping agent is a metered liability. And some actions — committing a payment, agreeing to
a contract change — are simply not delegable to a model unsupervised.

### Architecture decisions

The load-bearing decision was to split the system in two: an **outer durable workflow** owns the
call's lifecycle, and an **inner agent loop** owns the conversation. This is the durable-execution
pattern from [chapter 05](05-memory-state-and-durable-execution.md). The outer workflow is plain,
inspectable orchestration code — it persists state at every step, so a crash mid-call resumes from the
last checkpoint rather than restarting. The inner loop is where the model drives: it listens, decides,
and speaks, but it runs *inside* the workflow's rails, not as the system's top-level controller. The
team explicitly did not make the agent the orchestrator; per the
[decision framework](02-decision-framework.md), they kept the deterministic lifecycle in code and gave
the model only the genuinely open-ended part — the conversation.

Two controls made it safe to operate. First, **HITL gates** on the non-delegable actions: any
state-changing commit (payment, contract) paused the workflow and routed to a human for approval
before the agent could proceed. Second, a **per-task budget cap** enforced before each turn, not after
— if a call exceeded its token or wall-clock allowance, the workflow ended the call and escalated
rather than looping. The result was a reduction in average handle time of around 40% _(illustrative —
sanitized; verify nothing here as a benchmark)_ against the human-only baseline, with
the caveat that the figure folds in the deflection of simple calls and says nothing about the hard
ones.

### What we'd build today

We'd keep the outer/inner split exactly — it is the part that aged well — and invest harder in the
parts that didn't. We'd make every side-effecting tool idempotent from day one, keyed on a call id, so
a workflow retry can never double-charge or double-book. We'd treat the budget cap as a first-class
SLO with a dashboard, not a config constant, and emit OpenTelemetry GenAI traces per turn so a slow
call is a flame graph rather than a mystery. And we'd write the escalation path as a tested runbook
before launch, not after the first incident taught us we needed one. Because the agent acts unattended
on outbound contact, we'd classify it on the [capability-tier ladder](../templates/capability-tier-ladder.md)
and wire the **EU AI Act** Articles 11/12/14 (technical docs, immutable audit log, human oversight) in
from the start ([chapter 12](12-eu-ai-act-as-architecture.md)) rather than retrofitting them under a
deadline.

### What we'd avoid

We would not let the agent own the control flow — an early prototype made the model the orchestrator
and it could not reliably resume a dropped call, because conversational state and durable state were
the same thing and neither survived a restart. We'd avoid an after-the-fact cost alert in place of a
pre-execution cap; the prototype's first runaway loop burned through an _illustrative_ multiple of a
normal call's budget before anyone noticed. And we'd avoid gating *nothing* — the temptation to let the
agent "just confirm the small stuff" erodes until it is confirming things that move money.

## Case study 2 — AIGist24 AI Readiness Assessment agent (Python)

### Situation

AIGist24 built an agent that produces an "AI Readiness Assessment" — a structured report synthesizing
a target organization's public posture across many sources into a graded, cited brief. The work is
breadth-first: gather from many weakly-coupled sources, then synthesize. The risk is specific to
synthesis: a report that reads fluently but cites things the sources never said is worse than no
report, because it is confidently wrong and a human reader trusts the format.

### Architecture decisions

Because the task is breadth-first and parallelizable, this is the case where multi-agent earns its
keep ([decision framework](02-decision-framework.md)). The team used an **orchestrator-worker**
shape: an orchestrator decomposes the assessment into independent research questions, dispatches a
worker per question to gather and summarize its slice, and then synthesizes the workers' artifacts
into the final brief. The workers are weakly coupled by design — each owns a bounded sub-question — so
they parallelize cleanly without the inter-agent misalignment that sinks tightly-dependent
multi-agent systems.

The decision that defined the product was making **groundedness evals** a release gate, not a nicety
([chapter 13](13-evaluations.md)). Every claim in the synthesized report must be supported by a
retrieved source the system can point to; an LLM-as-judge scores each claim for groundedness against
its cited evidence, and a report below the groundedness threshold is rejected before it reaches a
reader. The judge itself was validated against a human-labeled sample so its scores meant something.
The illustrative groundedness figure on the golden set sat around 92% _(illustrative — sanitized;
verify nothing here as a benchmark)_, which is the right framing — a number on a labeled internal set,
not a claim about the world.

### What we'd build today

We'd sample production reports back into the eval set continuously — every report a human flagged as
ungrounded becomes a new golden case, closing the eval/observability loop
([chapter 13](13-evaluations.md)). We'd keep the orchestrator-worker shape but bound it harder: a hard
cap on workers per assessment, because an orchestrator with discretion over fan-out is a cost surface
that a single ambiguous request can blow open. And we'd separate the groundedness judge from the
generator entirely — different prompts, ideally different model tiers — so the system grading the work
is not the system that produced it.

### What we'd avoid

We would not skip judge validation. An unvalidated LLM-as-judge is a second hallucination risk wearing
a quality-gate costume, and a groundedness number from an uncalibrated judge is theater. We'd avoid
letting workers share mutable state — the early version had workers writing into a common scratchpad
and producing contradictory claims, exactly the inter-agent misalignment the
[decision framework](02-decision-framework.md) warns about; artifact handoff (each worker returns a
self-contained summary) fixed it. And we'd avoid treating the fluent final draft as the deliverable:
the deliverable is the *grounded* draft, and without the eval gate the two are indistinguishable to a
reader until the citation that was never in the source costs someone their credibility.
