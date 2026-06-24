# Human-in-the-Loop (HITL) Policy

**Purpose:** Decide which agent actions a human must approve before they execute, mapped to the capability tier, so autonomy never outruns accountability.
**When to use:** Whenever an agent can take a consequential action, and again every time you promote its tier or add a write/spend/send tool.
**How to fill:** Copy this file into your repo, replace every `{{PLACEHOLDER}}`, and delete the _italic guidance_.

---

## 1. Principle

> A human is in the loop for any action whose cost of being wrong exceeds the cost of a person reading it first. Approval gates are placed by consequence, not by how confident the model sounds.

_Confidence is not calibration. The model is most fluent exactly when it is most wrong; gate on blast radius, never on tone._

## 2. Tier → default oversight

_Anchored to `capability-tier-ladder.md`. The tier sets the default; section 3 can only tighten it, never loosen it._

| Tier | Name | EU AI Act risk class | Default oversight |
|------|------|----------------------|-------------------|
| L0 | Suggest-only | minimal | Human takes every consequential action; agent only drafts |
| L1 | Act-with-approval | limited | Human approves each action before execution |
| L2 | Act-with-guardrails | limited | Agent acts inside hard pre-execution limits; human reviews after the fact |
| L3 | Act-autonomously | high-risk | Agent acts unattended in a bounded domain; HITL only on flagged exceptions |
| L4 | Self-directed | prohibited | Not deployed |

## 3. Action class → approval matrix

| Action class | Example | Risk | Approval | Approver role | SLA |
|--------------|---------|------|----------|---------------|-----|
| Read-only | look up an order | low | auto | — | — |
| Reversible write | update a draft, tag a ticket | low | auto (logged) | — | — |
| Customer-facing send | email / chat to a user | medium | {{auto / human-approve}} | {{support lead}} | {{e.g. 15 min}} |
| Spend below cap | refund ≤ {{$cap}} | medium | auto within cap | — | — |
| Spend above cap | refund > {{$cap}} | high | human-approve | {{finance approver}} | {{e.g. 1 hr}} |
| Irreversible / destructive | delete data, cancel contract | high | two-person | {{owner + manager}} | {{e.g. 2 hr}} |
| Privilege or scope change | grant access, change a role | critical | two-person | {{security + owner}} | {{e.g. 30 min}} |
| Lethal-trifecta action | external action while handling untrusted input + private data | critical | human-approve (mandatory) | {{security}} | {{e.g. 30 min}} |

_The **lethal trifecta** — untrusted input + access to private data + the ability to externally communicate — is the prompt-injection exfiltration path. When all three meet in one action, an auto path is a breach waiting to happen. Break the trifecta or gate it with a human; there is no third option._

## 4. Escalation when the approver is unavailable

- **Primary approver:** {{role}} → **Backup:** {{role}} → **Break-glass:** {{role}}
- **If no approver responds within SLA:** the action {{does NOT execute — it queues / expires}}. _The default is deny. A pending high-risk action never auto-fires on timeout._
- **Break-glass:** {{who can override, what they must record, who is notified within {{N}} min}}

_Timeout-to-execute turns your gate into a delay. The only safe timeout behaviour for a consequential action is timeout-to-deny._

## 5. The reviewer's job (approval is NOT a rubber stamp)

Before approving, the reviewer must confirm:

- [ ] **Intent matches action** — the tool call does what the user actually asked, not a plausible-looking neighbour.
- [ ] **Inputs are sane** — amounts, recipients, IDs, scopes are in range and point where they should.
- [ ] **No injection smell** — nothing in the agent's context is instructing it to act against the user (especially if it processed untrusted content).
- [ ] **Reversibility understood** — the reviewer knows whether this can be undone, and at what cost.
- [ ] **Within the user's entitlement** — the requester is allowed to have this outcome.

_An approver who clicks "approve" on the agent's summary without checking the raw action is a liability, not a control. The summary is written by the thing you are guarding against. Review the actual call._

## 6. Audit logging

Every approve **and** reject is logged, immutably:

| Field | Captured |
|-------|----------|
| Action + full raw payload | {{yes}} |
| Decision | approve / reject |
| Reason | {{required free-text — a reject with no reason is rejected}} |
| Approver identity | {{authenticated, not shared}} |
| Timestamp + latency-to-decision | {{yes}} |
| Agent run / trace id | {{links the decision to the run}} |

_Log rejects as carefully as approvals. The rejects are your richest eval data and your early-warning system — a spike in rejects means the agent is drifting toward the boundary. Feed them back into `eval-plan-template.md`._

## 7. Review

- **Owner:** {{name / team}}
- **Cadence:** {{quarterly, or after any incident}}
- **Last reviewed:** {{date — _as of {{month year}} — verify before relying_}}
