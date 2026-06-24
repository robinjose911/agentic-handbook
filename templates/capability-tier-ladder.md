# Capability Tier Ladder

**Purpose:** Classify how much autonomy an agent has on a five-rung ladder (L0–L4) and map each rung to
an EU AI Act risk class, so "how autonomous is it?" has one answer everyone uses. This is the **T**
(Trust) anchor in AGENTIC and the spine of the whole handbook.
**When to use:** When you scope a new agent, when you propose raising its autonomy, and in any
board/procurement review that needs a shared risk vocabulary.
**How to fill:** This is the canonical reference table — copy it as-is. To classify an agent, find the
highest rung whose criteria it meets, then carry that rung + risk class into its
[`agent-design-spec.md`](agent-design-spec.md) and [`human-in-the-loop-policy.md`](human-in-the-loop-policy.md).

---

![Capability tier ladder L0–L4](../assets/diagrams/09-capability-tier-ladder.png)

## The ladder (canonical mapping)

> This table is the single source of truth. The same mapping appears in the
> `09-capability-tier-ladder` diagram, chapter 12 (_EU AI Act as architecture_), and the README — a
> drift between any of them is a failing test (`test_capability_ladder.py`).

| Tier | Name | Criteria | EU AI Act risk class |
|------|------|----------|----------------------|
| L0 | Suggest-only | Drafts and suggestions; a human takes every consequential action. | minimal |
| L1 | Act-with-approval | Agent proposes actions; a human approves each before execution. | limited |
| L2 | Act-with-guardrails | Agent acts inside hard, pre-execution policy limits; humans review after the fact. | limited |
| L3 | Act-autonomously | Agent acts unattended within a bounded domain; HITL only on flagged exceptions. | high-risk |
| L4 | Self-directed | Agent sets and revises its own goals across domains without scoped human oversight. | prohibited |

_The EU AI Act risk classes above are this handbook's architectural mapping, not legal advice. The Act
classifies by **use case and context**, not autonomy alone — a low-autonomy agent in a high-stakes
domain (hiring, credit, medical) can still be high-risk. Treat the risk class as the **floor** the
agent's domain may raise. See chapter 12. **_As of {{month year}} — verify against current EU AI Act
guidance before relying._**_

## How to classify

1. Read the criteria top-down; stop at the **highest** rung the agent can satisfy in production.
2. Raise the risk class if the **domain** is sensitive (Annex III use cases: employment, essential
   services, law enforcement, etc.) regardless of tier.
3. Record the rung + risk class in the agent's design spec. Promotions require the evals to hold at the
   current tier first.

## What each rung demands (controls that must exist before you operate there)

| Tier | Minimum controls before you ship at this tier |
|------|-----------------------------------------------|
| L0 | Output review by a human; basic logging. |
| L1 | Per-action approval gate; approver role + SLA defined; audit log of approve/reject + reason. |
| L2 | Hard pre-execution guardrails (budget cap, allowlist, scope limits); post-hoc review; kill switch. |
| L3 | Eval gate held; exception-based HITL; immutable audit trail; on-call + escalation runbook; incident plan. |
| L4 | **Do not operate.** Redesign the scope so the agent is bounded — L4 is prohibited in this handbook's stance. |

## Promotion checklist (moving up a rung)

- [ ] Evals pass at the current tier with margin (link the [`eval-plan-template.md`](eval-plan-template.md)).
- [ ] The new tier's controls (row above) all exist and are tested.
- [ ] The [`agent-risk-register.md`](agent-risk-register.md) re-rates residual risk at the new tier.
- [ ] The EU AI Act risk class is re-checked against the domain (chapter 12).
- [ ] Owner + reviewer sign-off recorded with a date.
