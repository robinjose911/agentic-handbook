# Agent Incident Postmortem

**Purpose:** Reconstruct, blamelessly, how an agent failed in production — what it did, what it should have done, why every guardrail missed it — and turn that into permanent eval and threat-model coverage.
**When to use:** After any production agent incident: a wrongful action, a runaway cost, a data exposure, a breached SLA, or a near-miss caught only by luck.
**How to fill:** Copy this file into your repo, replace every `{{PLACEHOLDER}}`, and delete the _italic guidance_.

---

## 0. Blameless statement

> This document examines a system that allowed a mistake, not a person who made one. Everyone acted on the information and tooling they had. The output is a stronger system, not a list of who to blame.

## 1. Summary

| Field | Value |
|-------|-------|
| Incident ID | {{INC-YYYY-NNN}} |
| Date / duration | {{detection → resolution, with timezone}} |
| Severity | {{SEV1 / SEV2 / SEV3}} |
| Agent + version | {{agent name, model + prompt version}} |
| One-line summary | {{what happened, in plain language}} |
| Status | {{mitigated / resolved / monitoring}} |

## 2. Impact

- **Users affected:** {{count / segment}}
- **Cost:** {{$ spent, refunds, wasted compute}} — _self-reported / illustrative_
- **Data:** {{what was exposed, sent, deleted, or corrupted — and to whom}}
- **Trust / compliance:** {{SLA breach, regulatory exposure, reputational hit}}
- **Blast radius:** {{contained to / spread to}}

## 3. Timeline

_All times one timezone. Detection → mitigation → resolution. Be specific; vague timelines hide the slow link._

| Time | Event |
|------|-------|
| {{t0}} | Trigger condition entered the system {{e.g. malicious input arrived / model update rolled out}} |
| {{t1}} | Agent took the wrong action {{what, and what it touched}} |
| {{t2}} | **Detected** by {{alert / customer report / human review}} — _gap from t1 to here is your detection latency_ |
| {{t3}} | **Mitigated** {{kill switch pulled / tool disabled / traffic stopped}} |
| {{t4}} | **Resolved** {{root cause fixed and verified}} |

## 4. What the agent did vs. should have done

| | Actual | Should have |
|--|--------|-------------|
| Decision | {{the call the agent made}} | {{the correct call}} |
| Tool use | {{tool + args it invoked}} | {{tool + args, or "should have refused / escalated"}} |
| Reasoning trace | {{what the trace shows it "believed"}} | {{where the reasoning first went wrong}} |

_Anchor this in the actual run trace, not a reconstruction from memory. The first wrong step matters more than the final loud one._

## 5. Root cause(s)

> {{The technical and systemic cause. Push past the proximate trigger: not "the model hallucinated a refund" but "untrusted ticket text reached a tool with no spend cap and no HITL gate." Use 5-whys; stop when you reach something you can actually change.}}

## 6. Contributing factors

- {{e.g. spend cap was advisory, not enforced pre-call}}
- {{e.g. the eval set had no adversarial / injection cases}}
- {{e.g. alerting fired on errors but not on anomalous spend}}
- {{e.g. the approver rubber-stamped the agent's summary without the raw payload}}

## 7. Why the defenses didn't catch it

_For each layer, state honestly why it missed. "We didn't have one" is a valid — and common — answer._

| Defense layer | Present? | Why it missed |
|---------------|----------|---------------|
| Input / output guardrails | {{yes/no}} | {{...}} |
| Tool contract validation | {{yes/no}} | {{cap was post-call, not pre-call}} |
| Eval coverage | {{yes/no}} | {{this case was not in the golden set}} |
| HITL gate | {{yes/no}} | {{action class was set to auto / approver didn't check the raw call}} |
| Observability / alerting | {{yes/no}} | {{no alert on this signal}} |

## 8. Action items

_Every item has an owner and a date. "Improve monitoring" is not an action item; "add a spend-anomaly alert at >2× baseline, owned by X, due Y" is._

| # | Action | Type | Owner | Due | Status |
|---|--------|------|-------|-----|--------|
| 1 | {{enforce spend cap pre-call in the tool contract}} | prevent | {{owner}} | {{date}} | {{open}} |
| 2 | {{add the failing input as a permanent eval case}} | detect | {{owner}} | {{date}} | {{open}} |
| 3 | {{add spend-anomaly alert}} | detect | {{owner}} | {{date}} | {{open}} |
| 4 | {{move this action class to human-approve}} | mitigate | {{owner}} | {{date}} | {{open}} |

## 9. Feedback into the system

This postmortem is not done until these land:

- **Eval set** (`eval-plan-template.md`): the triggering input is now a permanent regression case, expected to fail the old build and pass the fixed one. _If the eval can't reproduce the incident, you haven't found the root cause._
- **Risk register** (`agent-risk-register.md`): {{new row added / existing row re-scored — likelihood and impact updated to reflect that this can and did happen}}.
- **Threat model:** {{the attack path or failure mode added, so design reviews catch its cousins}}.
- **HITL policy** (`human-in-the-loop-policy.md`): {{action-class reclassified, if approval should have been required}}.

## 10. Lessons

> {{The transferable insight — the thing another team building a different agent should learn from this. One or two sentences. If there isn't one, the root cause analysis isn't finished.}}

---

- **Author:** {{name}} · **Reviewers:** {{names}}
- **Last updated:** {{date — _as of {{month year}} — verify before relying_}}
