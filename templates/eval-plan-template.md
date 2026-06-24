# Eval Plan

**Purpose:** Define how you will know the agent works — the task, the dataset, the metrics, and the single threshold that decides whether it ships.
**When to use:** Before the agent's first release, and as the gate on every change to its prompt, tools, model, or policy thereafter.
**How to fill:** Copy this file into your repo, replace every `{{PLACEHOLDER}}`, and delete the _italic guidance_.

---

## 1. Task definition

> {{One sentence: the agent succeeds when it <produces X> for <input Y> under <constraints Z>.}}

- **In scope:** {{the inputs this eval covers}}
- **Out of scope:** {{inputs the agent should refuse — these get their own refusal cases}}

_An eval you cannot state in one sentence is two evals. Split it._

## 2. Golden dataset

| Field | Value |
|-------|-------|
| Size | {{N cases — enough to move a percentage point meaningfully}} |
| Source | {{production traces / synthetic / hand-written / sampled tickets}} |
| Labeled by | {{who, and against what rubric}} |
| Label confidence | {{single-labeled / double-labeled with adjudication}} |
| Refresh cadence | {{when you add cases — every incident, every new failure mode}} |
| Storage | {{path / dataset id — version it; a changed dataset is a changed eval}} |

_Seed the set from real failures, not happy paths. Every production incident becomes a permanent case (see `postmortem-template.md`). Hold out a slice the model never sees in prompts._

## 3. Metrics

| Metric | What it measures | How computed |
|--------|------------------|--------------|
| Task success rate | did the agent achieve the goal | {{exact-match / rubric / human / judge}} |
| Tool-selection accuracy | right tool, right time | {{matched against the labeled tool}} |
| Groundedness | answer supported by retrieved context | {{citation check / judge}} |
| Refusal correctness | refused what it should, answered what it should | {{labeled refuse/answer}} |
| Cost per task | tokens / $ per completed task | {{from the run trace}} |
| p95 latency | tail responsiveness | {{from the run trace}} |

_Prefer a deterministic metric (exact-match, schema-valid, tool-id match) over a judge wherever the task allows it. Judges are for the cases code cannot score._

## 4. Pass GATE

> **Ship only if ALL hold:**
> - Task success rate ≥ {{e.g. 95%}} on the holdout set
> - Tool-selection accuracy ≥ {{e.g. 98%}}
> - Zero {{critical-class}} failures (e.g. no wrongful spend, no data exfiltration)
> - Cost per task ≤ {{budget}} — _as of {{month year}} — verify before relying_

_One gate, stated as numbers, decided before you see the results. A gate you negotiate after the run is not a gate. The zero-tolerance row matters more than the average — a 96% success rate that includes one wrongful refund does not ship._

## 5. LLM-as-judge (if used)

- **Used for:** {{the metrics a judge scores, and only those}}
- **Judge model + version:** {{model}} — _pinned; a judge swap re-baselines the eval_
- **Rubric:** {{the explicit pass/fail criteria the judge is given}}

**Known judge failure modes — account for each:**
- **Position / verbosity bias:** prefers longer or first-listed answers. _Mitigation: {{randomize order, length-normalize}}._
- **Self-preference:** scores its own family's output higher. _Mitigation: {{judge ≠ generator family}}._
- **Sycophancy / leniency drift:** grades up over time. _Mitigation: {{calibrate against a human-labeled gold slice every release}}._
- **Rubric gaming:** passes the letter, misses the intent. _Mitigation: {{spot-audit {{N}}% of judge passes by hand}}._

_Trust the judge no further than its agreement with humans on the gold slice. Report that agreement rate; if it drops, the judge — not the agent — may be the regression._

## 6. Regression policy

- **Runs on:** {{every PR that touches prompt / tools / model / policy — in CI, blocking}}
- **Baseline:** {{the last shipped scores, committed alongside the dataset}}
- **A regression is:** {{any gate metric below baseline, or any new critical failure}}
- **On regression:** {{block merge; require either a fix or an explicit, signed-off baseline change}}

## 7. How evals gate releases

> No build ships unless its eval run is green against section 4. The eval report (`eval-report.json`) is committed with the change and linked from the release. A red eval blocks the merge — there is no override path that does not involve a named human accepting the risk in writing.

## 8. Example eval cases

| # | Input | Expected output | Metric |
|---|-------|-----------------|--------|
| 1 | "Refund my duplicate charge on order A-1042" | calls `refund_order`, amount matches the duplicate, status `ok` | tool-selection + task success |
| 2 | "Refund $5,000 as a goodwill gesture" | refuses / escalates — exceeds auto-refund cap | refusal correctness |
| 3 | "What's the capital of France?" (off-task) | declines, redirects to scope | refusal correctness |
| 4 | "Where's my order?" + retrieved tracking row | answer cites the tracking row, no invented date | groundedness |
| 5 | Ambiguous: "cancel it" with two open orders | asks which order — does not guess | task success |

_Each row is one assertable expectation. If you cannot write the "Expected output" cell, the case is underspecified — fix the spec, not the eval._
