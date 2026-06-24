# 09 · Model selection for roles

Most teams pick one model and route everything through it. That is the expensive mistake. A real
agent system has *roles* — an orchestrator that plans and decides, workers that execute narrow steps,
a judge that scores outputs, a router that triages — and those roles have radically different
requirements. Treating "which model" as a single global setting leaves both money and quality on the
table: you overpay frontier rates for trivial sub-steps and, just as often, you starve the one role
that actually needs the strongest model. This chapter is about matching model capability to role
economics deliberately.

## Roles have different jobs, so they need different models

The load-bearing distinction is **orchestrator versus worker**.

The **orchestrator** owns the hard part: decomposing an ambiguous goal, sequencing steps, deciding
when the work is done, and recovering when a sub-step fails. This is the role where reasoning depth
and long-horizon coherence pay for themselves, and it is the role where you should spend on the
strongest model you can justify. The orchestrator's job is judgement under uncertainty, and a cheaper
model that loses the plot two steps in poisons everything downstream.

**Workers** do the opposite: a narrow, well-specified task — extract these fields, summarize this
chunk, call this tool, transform this record. The contract is tight, the context is bounded, and the
output is checkable. Here a smaller, faster, cheaper model is not a compromise; it is the correct
engineering choice. Workers run in volume and in parallel, so their per-call cost dominates your bill,
and their narrow scope means a capable small model matches the frontier on exactly the work you give
them.

The empirical case for splitting these roles is strong. Anthropic's multi-agent research system
documents an architecture where a **strong orchestrator delegated to cheaper sub-agents** — an Opus
lead with Sonnet workers — and the multi-agent configuration beat single-agent Opus by roughly
**90.2%** _(self-reported — verify)_ on their internal research evaluation
([Anthropic multi-agent research](../references.md#anthropic-multi-agent-research)). Read that twice:
the configuration that spread work across *cheaper* workers was also the *better* one. The mechanism is parallelism and context
hygiene — each worker gets a clean, narrow context instead of one model carrying the whole sprawling
state — not raw horsepower. This is the central result that should reshape how you assign models.

Two more roles round out the catalog. A **judge / evaluator** scores or critiques outputs; it often
needs orchestrator-grade reasoning because grading is as hard as generating, but it runs offline or
out-of-band, so latency matters less. A **router** triages incoming requests to the right model or
path; it should be the cheapest, fastest model you have, because it runs on every request and any
latency it adds is paid by every user. Routing easy queries to small models and only escalating hard
ones to the frontier is itself a documented cost lever
([RouteLLM](../references.md#routellm)).

## The orchestrator ceiling, and how to reason about it

How ambitious can the orchestrator be? The practical ceiling is set by how long a coherent task a
frontier model can actually sustain. METR tracks this directly: as of their February 2026 reading, a
frontier model reaches a **~14.5-hour 50%-task-time-horizon** _(self-reported, as of June 2026 —
verify before relying)_ ([METR time-horizon](../references.md#metr-horizon)) — meaning tasks that take
a human up to roughly that long, the model completes about half the time. That number is your design
budget. It says a strong orchestrator can credibly own multi-step work spanning hours of equivalent
human effort, but the 50% qualifier (verify) is the warning label: at the edge of the horizon you are flipping
a coin, so checkpoint, gate, and verify rather than handing the orchestrator a long leash and hoping.
Scope the orchestrator's autonomy *inside* the horizon, not at it.

This reframes model selection as a horizon question. If your task sits comfortably below the
orchestrator's reliable range, you can lean on autonomy and spend less on oversight. If it sits near
or beyond the horizon, no model choice rescues you — you decompose the task into shorter, verifiable
sub-tasks (which is the worker pattern again) and rebuild reliability from checkpoints.

## Making the tradeoff a real decision

Cost-quality is a curve, not a point, and you should treat it as one. Three moves operationalize it:

**Assign models per role, in config, and measure each.** Don't hardcode one model. Make the model a
per-role setting so you can A/B a cheaper worker without touching the orchestrator. The
[build-vs-buy harness template](../templates/build-vs-buy-harness.md) is built for exactly this:
hold the task fixed, swap the model, and read success rate, cost, and latency side by side. The
decision is never "is model X good?" — it is "is model X good *enough for this role* at this price?"

**Trade down workers aggressively, trade down the orchestrator never (without evidence).** The
asymmetry matters. A worker that drops from 99% to 97% (illustrative) on a checkable task at a fifth of the cost is
usually a win, because your verification layer catches the misses. An orchestrator that degrades
fails *silently and globally* — it makes a bad plan and every worker dutifully executes it. Cut worker
cost first and hardest; touch the orchestrator only with eval data in hand.

**Account for the full cost stack, not the sticker price.** Per-token price is one input. The number
of steps, retries, context size, tool round-trips, and the parallel fan-out all multiply it, and a
"cheaper" model that needs three attempts is not cheaper. Model selection only makes sense alongside
the rest of the spend, which is the subject of [chapter 15](15-cost-stack.md); read the two together,
because a model choice that ignores step count and retries is a number, not a decision.

The discipline is simple to state and easy to skip: name your roles, match each to the cheapest model
that clears its bar, spend the savings on a strong orchestrator and good evals, and re-measure when
the models change — which, as of mid-2026, is roughly monthly. One global model is the configuration
you settle for when you haven't done this work yet.
