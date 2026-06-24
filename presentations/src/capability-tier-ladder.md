# Capability Tier Ladder — board one-pager

How autonomous is the agent, and what risk does that carry? Five rungs, mapped to EU AI Act risk
classes. This is the shared vocabulary for any agent go/no-go decision.

## The ladder

| Tier | Name | Criteria | EU AI Act risk class |
|------|------|----------|----------------------|
| L0 | Suggest-only | Drafts and suggestions; a human takes every consequential action. | minimal |
| L1 | Act-with-approval | Agent proposes actions; a human approves each before execution. | limited |
| L2 | Act-with-guardrails | Agent acts inside hard, pre-execution policy limits; humans review after the fact. | limited |
| L3 | Act-autonomously | Agent acts unattended within a bounded domain; HITL only on flagged exceptions. | high-risk |
| L4 | Self-directed | Agent sets and revises its own goals across domains without scoped human oversight. | prohibited |

## How to read it

- The risk class is the FLOOR, not the ceiling. A low-autonomy agent in a sensitive domain (hiring,
  credit, health, essential services) is high-risk regardless of tier.
- Promote a tier only after the evals hold at the current tier, the controls for the new tier exist,
  and the risk register is re-rated.
- L4 is prohibited in this handbook's stance: redesign the scope so the agent is bounded.

## What each rung demands

- L0: human review of output; basic logging.
- L1: per-action approval gate; approver role + SLA; audit log of approve/reject + reason.
- L2: hard pre-execution guardrails (budget cap, allowlist, scope); post-hoc review; kill switch.
- L3: eval gate held; exception-based human oversight; immutable audit trail; on-call + incident plan.

This mapping is canonical across the handbook — the template, the diagram, chapter 12, and the README
all say the same thing. A drift is a failing test.
