# 03 · Pattern catalog

Once [chapter 02](02-decision-framework.md) has told you *whether* to build an agent, this is the
catalog of *shapes* you build it from. Each pattern below gets a uniform block: when to use, when
**not** to, a one-line sketch, and the anti-pattern that bites teams who reach for it reflexively. The
golden rule from [Anthropic's "Building Effective Agents"](../references.md#anthropic-building-effective-agents)
holds throughout: prefer the simplest composition that works, and only add control flow to the *model*
when the task genuinely needs a runtime-chosen path. Record whichever shape you pick in an
[agent design spec](../templates/agent-design-spec.md) so the choice is reviewable, not folklore.

Almost every shape here is a variation on one core loop — the model proposes an action, a tool runs it,
the observation feeds back, and the model decides whether it is done.

![The core agent loop: model proposes, tool acts, observation feeds back](../assets/diagrams/01-agent-loop.png)

The first decision is always whether you even need that loop. A **workflow** wires the path between LLM
calls in *your* code; an **agent** lets the model own the path. Most production value lives on the
workflow side of this line.

![Workflow versus agent: who owns the control flow](../assets/diagrams/02-workflow-vs-agent.png)

## The five workflow patterns

These four-plus-one are the canonical compositions from
[Anthropic's catalog](../references.md#anthropic-building-effective-agents). They are *workflows*: you
own the control flow, so they are cheap to test and hard to surprise. Start here.

**Prompt chaining.** Decompose a task into a fixed sequence of LLM calls, each consuming the last
output, with optional programmatic gates between steps.
- *When to use:* the task splits cleanly into ordered subtasks where accuracy beats latency (outline →
  draft → polish; extract → validate → format).
- *When NOT:* the steps are not knowable in advance, or a single call already nails it.
- *Sketch:* `classify() → if valid → translate() → review()`.
- *Anti-pattern:* a ten-link chain where one mid-chain failure silently corrupts everything downstream
  because no gate checks the intermediate.

**Routing.** Classify the input, then dispatch to a specialized prompt, model, or tool. Separation of
concerns lets each branch be tuned independently.
- *When to use:* distinct input categories that each deserve different handling (refund vs. complaint
  vs. how-to), or routing easy queries to a cheap model.
- *When NOT:* categories overlap so much the classifier is a coin flip — fix the taxonomy first.
- *Sketch:* `route(query) → {billing | technical | escalate}`.
- *Anti-pattern:* a misrouted query that lands in a confidently-wrong branch with no fallback class.

![The router pattern: classify once, dispatch to a specialist](../assets/diagrams/03-router-pattern.png)

**Parallelization.** Run independent LLM calls concurrently, either *sectioning* a task into parts or
*voting* across N runs for confidence.
- *When to use:* subtasks are independent (parallel guardrail + answer), or you want diversity/voting on
  a hard judgement.
- *When NOT:* later steps depend on earlier ones — that is a chain, not a fan-out.
- *Sketch:* `gather(summarize(a), summarize(b), summarize(c)) → merge()`.
- *Anti-pattern:* voting to paper over a prompt that is wrong on average; three bad samples do not make
  a good one.

**Orchestrator-worker.** A lead LLM dynamically decomposes a task, spawns worker calls, and synthesizes
their results — the decomposition is decided at runtime, not hard-coded.
- *When to use:* you cannot predict the subtasks (multi-file code edits, breadth-first research across
  weakly-coupled sources), as in [Anthropic's multi-agent research system](../references.md#anthropic-multi-agent-research).
- *When NOT:* the subtasks are tightly dependent — [Cognition warns this fractures context](../references.md#cognition-dont-build-multi-agents).
- *Sketch:* `orchestrator.plan() → spawn N workers → synthesize()`.
- *Anti-pattern:* fan-out for tightly-coupled work, where workers make conflicting assumptions and the
  synthesizer cannot reconcile them — a [MAST](../references.md#mast-taxonomy)-class architectural failure.

**Evaluator-optimizer.** One LLM generates, a second evaluates against explicit criteria, and the loop
iterates until the evaluator passes it.
- *When to use:* you have clear evaluation criteria *and* iteration measurably helps (literary
  translation, complex search with refinement).
- *When NOT:* the evaluator is no better than the generator, or "good enough" is a single call away.
- *Sketch:* `while not good_enough: draft = gen(feedback); feedback = eval(draft)`.
- *Anti-pattern:* an unbounded refine loop with no step/cost cap — it polishes forever and burns budget.

![Evaluator-optimizer: generate, critique against criteria, iterate](../assets/diagrams/06-evaluator-optimizer.png)

## The agentic patterns

These give the *model* control flow. They are more capable and more dangerous; gate them behind the
autonomy rails from [chapter 02](02-decision-framework.md).

**ReAct (reason + act).** The base agent loop: the model interleaves a reasoning trace with tool calls,
reading each observation before the next action.
- *When to use:* the path depends on what the agent discovers; tools return signal it must reason over.
- *When NOT:* the steps are enumerable — use a workflow.
- *Sketch:* `loop: think → call_tool → observe → (done?)`.
- *Anti-pattern:* no loop budget, so a stuck agent retries the same failing call forever.

**Plan-and-solve (plan-then-execute).** The agent writes a full plan first, then executes the steps,
optionally replanning on failure — front-loading the reasoning.
- *When to use:* long-horizon tasks where a coherent upfront plan beats greedy step-by-step drift.
- *When NOT:* the environment changes so fast the plan is stale before step two.
- *Sketch:* `plan = make_plan(goal); for step in plan: execute(step)`.
- *Anti-pattern:* executing a stale plan rigidly with no replan trigger when reality diverges.

**Planner-executor.** A structural split: a planner agent/role produces the plan, a separate executor
role runs it. The contract between them is an explicit artifact.
- *When to use:* you want to test or swap the planner independently, or run a cheaper executor model.
- *When NOT:* the overhead of two roles buys nothing over a single ReAct loop.
- *Sketch:* `planner → plan artifact → executor → results`.
- *Anti-pattern:* a lossy handoff where the executor lacks the planner's context and improvises.

![Planner-executor: a plan artifact crosses an explicit boundary](../assets/diagrams/04-planner-executor.png)

**Supervisor-worker.** A supervisor agent routes turns to specialized worker agents and owns the shared
state — the multi-agent generalization of routing.
- *When to use:* breadth-first, weakly-coupled work where workers genuinely specialize, per the
  [2026 reconciliation](../references.md#cognition-multi-agents-working).
- *When NOT:* deep, dependent work — keep it single-agent.
- *Sketch:* `supervisor → {researcher | coder | reviewer} → supervisor`.
- *Anti-pattern:* a supervisor that loses the thread of shared state and lets workers diverge.

![Supervisor-worker: a supervisor routes turns to specialist workers](../assets/diagrams/05-supervisor-worker.png)

**Handoff.** One agent transfers the whole conversation (and context) to another that takes over fully,
rather than delegating a subtask.
- *When to use:* a clean ownership change — triage → specialist, or escalation to a human.
- *When NOT:* you need both agents' judgement on the same turn — that is orchestration.
- *Sketch:* `triage_agent → handoff(specialist_agent)`.
- *Anti-pattern:* a handoff that drops context, forcing the user to repeat themselves.

**Reflection.** The agent critiques its own output and revises — evaluator-optimizer collapsed into one
actor.
- *When to use:* the model can reliably spot its own errors (self-consistency, draft critique).
- *When NOT:* the model is blind to the failure class — self-grading just rubber-stamps it.
- *Sketch:* `draft → self_critique → revise`.
- *Anti-pattern:* sycophantic self-review that approves its own mistakes; prefer an *independent* evaluator.

**Agentic RAG.** Retrieval becomes a *tool the agent calls* — it decides when to search, reformulates
queries, and retrieves iteratively, instead of a single fixed retrieve-then-generate step.
- *When to use:* questions needing multi-hop or query reformulation a static pipeline cannot express.
- *When NOT:* one well-tuned retrieval answers the question — keep it a workflow.
- *Sketch:* `loop: (need more?) → search(reformulated_q) → read → answer`.
- *Anti-pattern:* unbounded retrieval that floods the context window with low-relevance chunks and
  drowns the signal.

Compose these freely — most real systems are a workflow skeleton with one agentic loop inside. Whatever
you choose, write it down in the [agent design spec](../templates/agent-design-spec.md) before you code.
