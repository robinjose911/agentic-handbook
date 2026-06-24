# Agent ROI Framework

**Purpose:** Justify (or kill) an agent on the numbers - quantify the value it creates against the full cost stack, not just token spend.
**When to use:** Before greenlighting any agent build, at each autonomy-tier raise, and on a fixed quarterly review cadence once it is live.
**How to fill:** Copy this file into your repo, replace every `{{PLACEHOLDER}}`, and delete the _italic guidance_.

---

## 1. Value hypothesis

_State the single mechanism by which this agent makes or saves money. One sentence. If you cannot, you do not have a business case yet._

> {{e.g. "Deflects 40% of tier-1 support tickets, freeing 3 FTE-equivalents of agent time per week."}}

Pick the dominant value lever (you may have more than one, but rank them):

| Lever | Unit of value | Baseline (today) | Target (with agent) | Annualized value |
|---|---|---|---|---|
| Time saved | {{hours/week × loaded $/hr}} | {{baseline}} | {{target}} | {{$/yr}} |
| Revenue uplift | {{conversions, ARPU}} | {{baseline}} | {{target}} | {{$/yr}} |
| Deflected cost | {{tickets, vendor fees, rework}} | {{baseline}} | {{target}} | {{$/yr}} |
| Quality / risk reduction | {{error rate, SLA penalties}} | {{baseline}} | {{target}} | {{$/yr}} |

_Use loaded labor cost (salary + benefits + overhead), not raw salary. Discount soft "productivity" claims hard - count only value you can measure and attribute._

**Gross annual value (V):** {{$ }}

## 2. The cost stack

_Most agents die in production on the costs people forget at proposal time: human review, eval upkeep, and incident risk. Fill every row, even with a rough number._

| Cost component | Driver | Unit cost | Volume / mo | Monthly cost | Annual cost |
|---|---|---|---|---|---|
| LLM tokens (in + out) | tokens/task × tasks | {{$/1M tok}} | {{tasks}} | {{$}} | {{$}} |
| Retrieval / embeddings / vector store | queries, storage | {{$}} | {{}} | {{$}} | {{$}} |
| Infra (compute, orchestration, logging) | runtime, traces | {{$}} | {{}} | {{$}} | {{$}} |
| Human-in-the-loop review | min/task × reviewer $/hr | {{$}} | {{reviewed tasks}} | {{$}} | {{$}} |
| Eval + monitoring upkeep | eng hrs/mo | {{$/hr}} | {{hrs}} | {{$}} | {{$}} |
| Maintenance (prompt/model drift, deps) | eng hrs/mo | {{$/hr}} | {{hrs}} | {{$}} | {{$}} |
| Incident / risk reserve | expected loss × probability | {{$}} | n/a | {{$}} | {{$}} |
| Vendor / licensing | seats, platform fee | {{$}} | n/a | {{$}} | {{$}} |

**Total annual cost (C):** {{$ }}

_The incident/risk reserve is the expected cost of the agent doing something wrong: a bad refund, a wrong answer that reaches a customer, a compliance miss. Estimate as (worst-case loss) × (annual probability). If this dominates the stack, you likely need a lower autonomy tier, not a bigger model._

## 3. Net ROI and break-even

> **Net annual value = V - C = {{$ }}**
> **ROI = (V - C) / C = {{% }}**
> **Payback period = (one-time build cost) / (monthly net) = {{months}}**

| Metric | Value |
|---|---|
| One-time build cost (eng + design + eval harness) | {{$}} |
| Monthly net (V/12 - C/12) | {{$}} |
| Break-even volume (tasks/mo to cover fixed cost) | {{tasks}} |
| Break-even date | {{month year}} |

_If payback is longer than your planning horizon, or break-even volume exceeds realistic demand, stop here. The honest answer is sometimes "not yet."_

## 4. Sensitivity analysis

_Single-point estimates lie. Stress the two variables that move most: task volume and model price. An agent that only pencils out at one exact volume is not a business case._

| Scenario | Volume | Token price | Annual cost (C) | Net (V - C) | Still worth it? |
|---|---|---|---|---|---|
| Base case | {{}} | {{}} | {{$}} | {{$}} | {{Y/N}} |
| Volume 2x | {{2×}} | same | {{$}} | {{$}} | {{Y/N}} |
| Volume 0.5x | {{0.5×}} | same | {{$}} | {{$}} | {{Y/N}} |
| Model price +50% | same | {{+50%}} | {{$}} | {{$}} | {{Y/N}} |
| Model price -50% | same | {{-50%}} | {{$}} | {{$}} | {{Y/N}} |
| Review rate doubles | same | same | {{$}} | {{$}} | {{Y/N}} |

_Model prices have trended down historically, but do not bank a future cut into today's decision - size the case on prices you pay now. Treat any assumed future price drop as upside, not the plan._

## 5. Do nothing / buy / build

_Always price the alternatives. The status quo is a real option and is often the right one._

| Option | One-time | Annual run | Time-to-value | Net value | Notes |
|---|---|---|---|---|---|
| Do nothing (status quo) | $0 | {{current cost}} | n/a | baseline | The number to beat |
| Buy (vendor / SaaS) | {{$}} | {{$}} | {{weeks}} | {{$}} | lock-in, less control |
| Build (in-house) | {{$}} | {{$}} | {{months}} | {{$}} | full control, you own upkeep |

_Run the structured comparison in [`build-vs-buy-harness.md`](./build-vs-buy-harness.md) before committing - this row is just the headline. A positive ROI vs "do nothing" can still lose to "buy."_

## 6. Kill criterion

_Decide now, in cold blood, the metric at which you switch this agent off. Pre-committing a kill line is what separates a portfolio from a graveyard of half-dead pilots._

> **We will turn this agent off if {{metric}} falls below/rises above {{threshold}} for {{duration}}, measured by {{owner/dashboard}}.**

| Trip condition | Threshold | Window | Action |
|---|---|---|---|
| Net monthly value | < {{$}} | {{2 consecutive months}} | Review then sunset |
| Task success rate | < {{%}} | {{rolling 2 weeks}} | Freeze + investigate |
| Cost-per-task | > {{$}} | {{rolling month}} | Throttle or kill |
| Human-review load | > {{% of tasks}} | {{1 month}} | Lower autonomy or kill |

_Tie the success/cost thresholds to your live SLOs - see [`agent-slo-definition.md`](./agent-slo-definition.md). The kill criterion is an exec commitment, not an aspiration; name the owner._

## 7. Worked example (illustrative)

_Synthetic example for a tier-1 support-deflection agent. Replace entirely - do not copy these numbers into your case._

**Value** _(illustrative figures - not a benchmark)_

| Lever | Calc | Annual value |
|---|---|---|
| Deflected tier-1 tickets | 1,200 tickets/mo × 30% × $6 handled cost | $25,920 |
| Reclaimed agent time | 3 hrs/day × $40/hr loaded × 250 days | $30,000 |
| **Gross value (V)** | | **$55,920** |

**Cost** _(illustrative figures - not a benchmark)_

| Component | Calc | Annual cost |
|---|---|---|
| LLM tokens | 360 deflected/mo × $0.04/task × 12 | $173 |
| Infra + logging | flat | $3,600 |
| HITL review (20% sampled) | 72/mo × 4 min × $40/hr × 12 | $2,304 |
| Eval + maintenance | 6 eng hrs/mo × $90/hr × 12 | $6,480 |
| Incident reserve | $5,000 worst case × 20% | $1,000 |
| **Total cost (C)** | | **$13,557** |

**Result** _(illustrative figures - not a benchmark)_: Net = $42,363/yr; ROI ~ 312%; one-time build $20,000 -> payback ~5.7 months. Break-even at ~290 deflected tickets/mo. Survives Volume 0.5x; fails if review rate exceeds ~60% of tasks.
