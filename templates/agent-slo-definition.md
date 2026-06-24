# Agent SLO Definition

**Purpose:** Define what "working" means for an agent in production as numbers you can alert on - service-level indicators, objectives, and an error budget that governs how fast you may ship.
**When to use:** Before an agent serves real traffic, and on every change that could move quality, latency, or cost.
**How to fill:** Copy this file into your repo, replace every `{{PLACEHOLDER}}`, and delete the _italic guidance_.

---

## 1. Scope

_Name the agent and the unit of work an SLO is measured over. "Task" must be defined precisely - a single user turn, a full resolved request, a batch job - or every metric below is ambiguous._

- **Agent:** {{name / version}}
- **A "task" is:** {{one user request resolved end-to-end, including tool calls}}
- **Owner / on-call:** {{team}}
- **Tier / autonomy level:** {{e.g. suggest-only / act-with-approval / autonomous}}

## 2. Service-level indicators (SLIs)

_The signals you actually measure. Each must be computable from logs/traces with no human in the loop, or it is not an SLI._

| SLI | Definition | How measured |
|---|---|---|
| Task success rate | % of tasks meeting the success definition | eval label / golden set / downstream signal |
| Latency p50 / p95 | end-to-end wall time per task | trace timestamps |
| Tool-error rate | % of tool calls returning error/timeout | tool spans |
| Escalation rate | % of tasks handed off to a human | handoff events |
| Cost-per-task | total token + infra spend / tasks | billing + task count |
| Groundedness / quality | % of outputs supported by retrieved evidence (or judge score) | grounding check / LLM-judge on sample |

_Define "success" explicitly and in advance - a measurable, attributable outcome, not vibes. If you sample (e.g. for quality), record the sample rate._

## 3. Targets, budgets, and windows

_The objective and its error budget. The error budget is the allowance of failure you accept - and the lever that governs release velocity. Pick a measurement window long enough to be stable, short enough to act on._

**Measurement window:** {{rolling 28 days}} - **Reporting cadence:** {{weekly}}

| SLI | SLO target | Error budget | What burns it |
|---|---|---|---|
| Task success rate | >= {{92%}} | {{8%}} of tasks may fail | each unsuccessful task |
| Latency p95 | <= {{8s}} | {{5%}} of tasks may exceed | each slow task |
| Tool-error rate | <= {{2%}} | {{2%}} of tool calls | each failed tool call |
| Escalation rate | <= {{15%}} | {{band, not pure budget}} | escalations above band |
| Cost-per-task | <= {{$0.12}} | {{spend cap}} | each task over target cost |
| Groundedness | >= {{90%}} | {{10%}} ungrounded | each unsupported output |

_Escalation and cost are often "bands" with both a floor and a ceiling - an escalation rate of zero can mean the agent is over-confident and unsafe, not excellent. Set both edges._

## 4. Alerting thresholds

_Alert on burn rate, not on a single bad task. Fast-burn pages; slow-burn opens a ticket. Tune so you catch a real regression before the budget is gone, without paging on noise._

| Condition | Threshold | Severity | Action |
|---|---|---|---|
| Fast burn | budget burning at >= {{14×}} normal over {{1h}} | Page | Open incident, see runbook |
| Slow burn | budget burning at >= {{3×}} normal over {{6h}} | Ticket | Investigate same day |
| SLO breached | any SLI past target over the window | High | Freeze changes (see §6) |
| Cost spike | cost-per-task > {{1.5×}} target over {{1h}} | Page | Throttle + investigate |
| Quality drop | groundedness/success down {{>5pts}} vs baseline | High | Roll back recent change |

_Wire these to [`escalation-runbook.md`](./escalation-runbook.md) so an alert lands on a defined response, not a guess._

## 5. Error-budget policy

_What the budget actually controls: your freedom to ship. Spell out the regime so the decision is automatic, not negotiated mid-incident._

- **Budget remaining:** ship normally. Experiment, raise autonomy within tier, iterate.
- **Budget < {{25%}}:** caution. Only changes that protect the SLO; extra review on prompt/model changes.
- **Budget exhausted:** **change freeze** on the agent - no feature work, no model swaps - until the SLO recovers over a full window. All effort goes to reliability.

## 6. When the budget is exhausted

_Pre-committed response. No debate during the incident - the order is decided now._

1. **Freeze changes.** Halt feature deploys and model/prompt swaps on this agent.
2. **Raise HITL.** Increase human-in-the-loop review (lower the autonomy tier) until success/quality recover.
3. **Roll back.** Revert to the last config/version that met the SLO.
4. **Root cause.** Diagnose before unfreezing; close with a postmortem ([`postmortem-template.md`](./postmortem-template.md)).
5. **Unfreeze** only after the SLO holds for a full measurement window.

## 7. Example SLI/SLO table (illustrative)

_Synthetic targets for a customer-support triage agent. Replace entirely - not benchmarks._

_(illustrative figures - not a benchmark)_

| SLI | Target | Window | Alert (page) at |
|---|---|---|---|
| Task success rate | >= 93% | 28d rolling | < 88% over 1h |
| Latency p95 | <= 6s | 28d rolling | > 10s over 15m |
| Tool-error rate | <= 1.5% | 28d rolling | > 5% over 30m |
| Escalation rate | 5%-18% (band) | 28d rolling | outside band over 6h |
| Cost-per-task | <= $0.10 | 28d rolling | > $0.15 over 1h |
| Groundedness (sampled 10%) | >= 92% | 28d rolling | < 85% over 6h |

**Error budget** _(illustrative)_: at 93% success target, ~7% of tasks may fail per 28-day window. Burn it faster than 14× and the on-call is paged; exhaust it and the agent enters change-freeze until success recovers over a full 28 days.
