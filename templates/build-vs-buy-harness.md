# Build vs Buy Decision Harness

**Purpose:** Force a structured, weighted decision on whether to build an agent in-house, buy a vendor product, or adopt a framework - instead of defaulting to whatever the loudest engineer prefers.
**When to use:** Once a [`roi-framework.md`](./roi-framework.md) pass clears the "do nothing" bar and you are choosing how to deliver.
**How to fill:** Copy this file into your repo, replace every `{{PLACEHOLDER}}`, and delete the _italic guidance_.

---

## 1. Define the options

_Name the concrete options on the table. Be specific - "buy" means a named product class, not a vague intention._

| Option | What it is | Rough cost shape |
|---|---|---|
| **Build** | {{in-house on raw SDK + your orchestration}} | high one-time, you own upkeep |
| **Buy** | {{managed vendor product / SaaS agent platform}} | subscription, fast start |
| **Framework** | {{adopt an open orchestration framework, host yourself}} | medium build, community upkeep |

_You may compare two options or all three. Drop any that are obviously non-viable and say why in one line._

## 2. Scoring dimensions and weights

_Set weights so they sum to 100. The weights encode your strategy: a regulated org weights compliance and data posture; a startup chasing a window weights time-to-value. Decide weights before you score - never after._

| # | Dimension | Why it matters | Weight (of 100) |
|---|---|---|---|
| 1 | Control / customization | Can you shape behavior, prompts, tools, and the roadmap? | {{20}} |
| 2 | Time-to-value | Weeks to first production value | {{15}} |
| 3 | Total cost of ownership (3-yr) | All-in build + run + upkeep, not sticker price | {{15}} |
| 4 | Data / security posture | Where data flows, residency, tenancy, retention | {{15}} |
| 5 | Lock-in / exit cost | How trapped are you if it goes wrong | {{10}} |
| 6 | Reliability + support | Uptime, SLAs, incident response, maturity | {{10}} |
| 7 | Compliance / EU AI Act fit | Risk-class fit, documentation, transparency obligations | {{10}} |
| 8 | Talent required | Do you have (and want to hold) the skills | {{5}} |
| | **Total** | | **100** |

## 3. Scoring key

_Score each option 1-5 per dimension. Be ruthless and evidence-based - a 5 means "demonstrably best in class," not "sounds fine."_

| Score | Meaning |
|---|---|
| 5 | Excellent - clearly the strongest option on this dimension |
| 4 | Good - meets the need with margin |
| 3 | Adequate - acceptable, some gaps |
| 2 | Weak - meets the bar only with effort/workarounds |
| 1 | Poor - a real liability on this dimension |

**Weighted score** for an option = sum over dimensions of `(score × weight) / 100`. Max possible = 5.0.

## 4. Score the options

_Fill the raw 1-5 score in each cell, then compute the weighted total. Keep a one-line justification per cell in your notes - the score is only as honest as the evidence behind it._

| Dimension (weight) | Build | Buy | Framework |
|---|---|---|---|
| Control / customization ({{20}}) | {{}} | {{}} | {{}} |
| Time-to-value ({{15}}) | {{}} | {{}} | {{}} |
| Total cost of ownership ({{15}}) | {{}} | {{}} | {{}} |
| Data / security posture ({{15}}) | {{}} | {{}} | {{}} |
| Lock-in / exit cost ({{10}}) | {{}} | {{}} | {{}} |
| Reliability + support ({{10}}) | {{}} | {{}} | {{}} |
| Compliance / EU AI Act fit ({{10}}) | {{}} | {{}} | {{}} |
| Talent required ({{5}}) | {{}} | {{}} | {{}} |
| **Weighted total (max 5.0)** | **{{}}** | **{{}}** | **{{}}** |

## 5. Decision rule

_The score informs; it does not decide. Apply the rule, then apply judgment - and write down where you overrode the number and why._

- **Pick the highest weighted total** unless it scores a **1 on any dimension you flagged as a hard gate**.
- **Hard gates** _(mark the dimensions where a score of 1-2 is disqualifying regardless of total)_: {{e.g. Data/security posture, Compliance/EU AI Act fit}}.
- **Margin rule:** if the top two are within **{{0.3}}** points, the score is a tie - decide on reversibility (Section 6) and strategic fit, not the decimals.
- **Override log:** _record any decision that contradicts the ranking and the reason._ {{none}}

> **Decision:** {{Build / Buy / Framework}} - **owner:** {{name}} - **date:** {{month year}} - **revisit:** {{date}}

## 6. Reversibility check

_The single most under-priced factor. A wrong-but-reversible choice is cheap; a right-but-irreversible one is a bet. Score how hard it is to switch later._

| Question | Build | Buy | Framework |
|---|---|---|---|
| Is the data export-able in an open format? | {{Y/N}} | {{Y/N}} | {{Y/N}} |
| Are prompts/configs portable off this stack? | {{Y/N}} | {{Y/N}} | {{Y/N}} |
| Is the model provider swappable? | {{Y/N}} | {{Y/N}} | {{Y/N}} |
| Contractual exit / notice period | {{n/a}} | {{months}} | {{n/a}} |
| Estimated switch cost (eng-months + $) | {{}} | {{}} | {{}} |
| **Reversibility rating (High/Med/Low)** | {{}} | {{}} | {{}} |

_Prefer Buy/Framework options that keep your data and prompts portable and the model provider swappable. If the cheapest option is a one-way door, price the door._

## 7. Worked example (illustrative)

_Synthetic scoring for an internal knowledge-assistant agent. Replace entirely - these are not benchmarks._

_(illustrative figures - not a benchmark)_

| Dimension (weight) | Build | Buy | Framework |
|---|---|---|---|
| Control / customization (20) | 5 | 2 | 4 |
| Time-to-value (15) | 2 | 5 | 3 |
| Total cost of ownership (15) | 3 | 3 | 4 |
| Data / security posture (15) | 5 | 3 | 4 |
| Lock-in / exit cost (10) | 5 | 2 | 4 |
| Reliability + support (10) | 3 | 5 | 3 |
| Compliance / EU AI Act fit (10) | 4 | 4 | 3 |
| Talent required (5) | 2 | 5 | 3 |
| **Weighted total** | **3.95** | **3.30** | **3.70** |

**Outcome** _(illustrative)_: Build leads on the score (3.95), and clears all hard gates (data posture 5, compliance 4). Buy wins time-to-value but scores 2 on lock-in - acceptable only if the data stays portable. Decision: Build, with a Framework fallback (within 0.3 is not triggered here; the gap is 0.25 vs Framework, so reversibility was the tiebreaker discussion - Build's High reversibility sealed it).
