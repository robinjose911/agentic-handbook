# 07 · CodeAct vs tool calls

There are three ways to let a model act on the world, and most teams default to the wrong one. You can
have the model emit **discrete JSON tool calls** (one function, one set of arguments, back to the
model). You can have it emit a **structured output** that your code consumes without any further model
turn. Or you can have it emit **code** — a short program in a real language — that runs in a sandbox
and returns its result. The third option is **CodeAct**, and the research is unambiguous that for a
specific shape of task it dominates the JSON-tool-calling loop
([Wang et al., "Executable Code Actions Elicit Better LLM Agents"](../references.md#codeact)).

This chapter is about choosing among the three. The choice is load-bearing because it sets your step
count, your token bill, your latency, and your blast radius — and because the wrong default quietly
multiplies all four.

## The three modes, and what each is for

**Discrete JSON tool calls** are the right default for *consequential, auditable, individually-gated*
actions. When the model wants to issue a refund, send an email, or write a row to a system of record,
you want exactly that intent surfaced as a typed payload your code validates before executing. Each
call is a checkpoint: you can log it, approve it, rate-limit it, and replay it. The contract for these
payloads is the subject of [chapter 04](04-tool-design-and-contracts.md), and the discipline there —
narrow schemas, validated arguments, idempotency keys — is exactly what makes JSON tool calls safe to
expose to an autonomous loop.

**Structured outputs** are for the terminal step where the model's job is to *produce data*, not act:
classify a ticket, extract fields, emit the final answer in a schema. No tool, no second turn, no
sandbox — just a constrained generation your code consumes. Reach for this whenever the model is the
last node in the graph and the deliverable is a typed object.

**CodeAct** is for the messy middle: many small steps, loops over collections, conditional logic,
data-wrangling, and chained transforms where the output of one step feeds the next. Instead of a
round-trip per step — model emits call, runtime executes, result goes back into context, model emits
the next call — the model writes one program that does the whole sequence and returns only the result.
The original CodeAct work reports up to **+20% absolute success rate** _(self-reported — verify)_ and
roughly **30% fewer interaction turns** _(self-reported — verify)_ versus JSON tool calling on the
same agent tasks ([CodeAct](../references.md#codeact)). The intuition is simple: code is the native
medium for composition. Loops, branches, intermediate variables, and library calls already exist in
Python; expressing them as a sequence of JSON envelopes is a lossy, expensive re-encoding.

The convergence is telling. HuggingFace's [smolagents](../references.md#smolagents) made "the agent
writes Python" its default execution model. Anthropic's Agent Skills and sandboxed code-execution
tooling push the same shape — give the model a real interpreter and a filesystem, not a hundred narrow
function wrappers. When independent teams arrive at the same architecture from different starting
points, it is worth treating as a signal rather than a fashion.

## The decision tree

Embed this in your design review and walk it top to bottom.

![CodeAct vs tool-calls decision tree](../assets/diagrams/12-codeact-decision.png)

**Start: is this the final, data-producing step?** If the model's output is the deliverable and no
further action follows, use a **structured output**. Done.

**Otherwise: does the action need an individual gate?** If the step is consequential and must be
logged, approved, or rate-limited on its own — a payment, an irreversible write, anything a human or
policy must sign off — use a **discrete JSON tool call** so the intent is a checkpoint. Do not bury a
refund inside a code blob where it can't be intercepted.

**Otherwise: is it many small steps, a loop, or data-wrangling — AND do you have a sandbox — AND is
the output verifiable?** If all three hold, use **CodeAct**. "Many small steps or a loop" is the
benefit (you collapse N round-trips into one). "A sandbox" is the safety precondition (untrusted
generated code must run isolated — no host network, no host filesystem, resource caps, a timeout). "A
verifiable output" is the trust precondition (you can assert on the return value, so a wrong program
fails loudly rather than silently corrupting state).

**If any of the three fail, fall back to discrete tool calls.** No sandbox means no CodeAct — running
model-authored code on your host is the kind of decision that ends up in a postmortem. An
unverifiable result means you can't tell a correct run from a plausible-looking wrong one, which is
worse than slower JSON calls you can inspect step by step.

A worked example sharpens the line. "Reconcile these 400 invoices against the ledger, flag mismatches
over $50 (illustrative), and summarize by vendor" is textbook CodeAct: a loop, arithmetic, filtering, grouping, a
verifiable summary, and nothing individually consequential. Doing it as 400+ JSON round-trips is slow,
expensive, and fragile. By contrast, "issue a refund for invoice #314" is one consequential action —
a discrete tool call with an idempotency key and an approval gate, never a line of generated code.

## What this costs you, and the caveats

CodeAct is not free. You inherit an execution-sandbox dependency — provisioning, isolation, egress
control, and lifecycle management of an interpreter per session — which is real operational surface
that JSON tool calls don't carry. You also widen the threat model: generated code is an untrusted
input, so the sandbox is a hard security boundary, not a convenience. Treat anything the model writes
as hostile by default and size the blast radius accordingly.

Two practical guards. First, give the sandbox a *curated* library surface, not the open internet — a
handful of vetted helpers the model can call beats letting it `pip install` at runtime. Second, keep
the consequential actions *outside* the sandbox as real tool calls the code can request but not
perform directly, so your approval and audit layer still sees them. The pattern that scales is a
CodeAct core for computation wrapped by discrete, gated tool calls for effects.

The honest summary: structured outputs for the terminal deliverable, discrete JSON tool calls for
anything you must gate or audit, and CodeAct for compute-heavy, loop-heavy, verifiable middle work
where a sandbox already exists. Default to tool calls; earn your way into CodeAct by clearing all
three preconditions. The +20% and 30%-fewer-steps figures _(self-reported — verify)_ are real, but
they are conditional on exactly the situation the decision tree describes — not a blanket license to
let the model run code.
