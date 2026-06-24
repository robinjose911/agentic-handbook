# 13 · Evaluations

You cannot improve what you cannot measure, and you cannot ship an agent you cannot measure. This is
the **E** (Evaluation) surface: the eval-driven development loop that turns "it seems to work" into a
number you defend to a board. It pairs with the [eval-plan template](../templates/eval-plan-template.md).

## Eval-driven development

The consensus loop is simple and unglamorous:

1. **Capture production traces** — real inputs and the agent's actual behavior
   ([chapter 14](14-observability-lite.md)).
2. **Annotate failures** — a human labels what went wrong and what "right" was.
3. **Convert to a dataset** — failures become golden cases with expected outcomes.
4. **Run as CI** — the eval set runs on every change, exactly like a test suite.
5. **Regression-gate** — a drop below the threshold blocks the merge.

The discipline is treating evals as **code, not a one-time report**. Tools like
[DeepEval](../references.md#deepeval) (pytest-style) and [Ragas](../references.md#ragas) (RAG-specific)
exist to make eval suites first-class; the [eval-plan template](../templates/eval-plan-template.md)
gives you the dataset + metric + gate structure.

## Benchmarks: useful, and easy to misread

Public benchmarks calibrate expectations but do not measure *your* task. Know the landscape, and the
caveats:

- [SWE-bench](../references.md#swe-bench) (Verified / Multimodal / Pro) — software-engineering tasks
  from real issues. The headline number is the most-quoted and least-transferable.
- [τ-bench](../references.md#tau-bench) — tool-agent tasks. The instructive caveat: an empty-response
  agent scores about 38% on τ-bench-Airline (_self-reported caveat — verify_), because partial-credit
  scoring rewards doing nothing. A benchmark number without its scoring rule is noise.
- Terminal-Bench, GAIA, WebArena, BrowseComp, OSWorld — each probes a different surface; none is a
  proxy for your production workload.

Quote any benchmark figure with its source and date, labeled _self-reported, as of June 2026 — verify
before relying_, and never let a vendor's headline stand in for your own eval.

## LLM-as-judge, and its failure modes

Using a model to grade a model scales evaluation, but the judge has known biases: **length bias**
(longer answers score higher), **position bias** (order of options sways the verdict), **sycophancy**
(agreeing with the candidate), and outright **gaming** — a chain-of-thought crafted to manipulate the
judge. The defenses:

- Pair the judge with **code-based assertions** (schema checks, exact-match where possible) so a fact
  is checked, not just vibed.
- **Calibrate the judge against humans** periodically; a judge is itself a model that drifts.
- Use **multiple independent judges** for high-stakes verdicts rather than one.

A single-judge-LLM eval with no code assertions is "eval theater" — it produces a number that feels
like rigor and isn't (see [chapter 17](17-anti-patterns.md)).

## The launch gate

Every agent ships behind a gate: a metric (task success rate, groundedness, tool-selection accuracy)
and a threshold it must hold, with the eval running on every change. The
[production-readiness checklist](../templates/production-readiness-checklist.md) treats a passing,
non-regressing eval as a hard go/no-go condition — and so should you.
