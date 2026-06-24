# Agent Escalation Runbook

**Purpose:** Give on-call a fast, pre-decided path when an agent misbehaves - contain, diagnose, mitigate, communicate - so nobody improvises a kill-switch during an incident.
**When to use:** The moment any trigger below fires; keep it open during the whole incident and hand off to a postmortem at the end.
**How to fill:** Copy this file into your repo, replace every `{{PLACEHOLDER}}`, and delete the _italic guidance_.

---

## 1. Triggers

_Any one of these opens an incident. Wire your alerts ([`agent-slo-definition.md`](./agent-slo-definition.md)) directly to this runbook so the trigger and the response are the same artifact._

| Trigger | Signal |
|---|---|
| **Cost spike** | cost-per-task or total spend over cap; runaway token burn |
| **Loop** | agent retrying / re-planning without progress; step count climbing |
| **Repeated tool failures** | a tool erroring/timing out above threshold; cascading retries |
| **Safety / guardrail trip** | policy filter fired, jailbreak/injection detected, disallowed action attempted |
| **User complaint** | report of harmful, wrong, or off-policy output reaching a user |
| **Data / exfil signal** | unexpected egress, sensitive data in output, lethal-trifecta path active |

## 2. Severity levels

_Set severity from blast radius and reversibility, not from how loud it feels. When in doubt, go one level higher._

| Sev | Definition | Examples | Response time | Who |
|---|---|---|---|---|
| **Sev-1** | Active harm, data exposure, or unbounded spend; reaches customers | exfiltration, harmful output to users, runaway cost | Immediate page | On-call + incident lead + {{exec}} |
| **Sev-2** | Degraded but contained; SLO breached; no external harm yet | success rate collapse, looping, tool outage | < {{15 min}} | On-call + owner |
| **Sev-3** | Minor / single-user; workaround exists | one bad answer, isolated tool error | < {{1 business day}} | Owner |

## 3. On-call decision tree

_Run in order. Contain before you diagnose - stop the bleeding first, understand it second. Never skip straight to "let me debug it live in prod."_

```
TRIGGER fires
   |
   v
[1] CONTAIN  --> Can it cause more harm/spend right now?
   |              YES -> hit the kill switch (§4) or lower autonomy / throttle
   |              NO  -> proceed
   v
[2] DIAGNOSE --> Pull traces, last config/model change, scope of impact
   |              (who/what is affected, since when, which version)
   v
[3] MITIGATE --> Roll back last change | raise HITL | disable offending tool/MCP server
   |              | tighten guardrail | reduce traffic
   v
[4] COMMUNICATE -> Notify stakeholders (§5); update status; set next checkpoint
   |
   v
RECOVER -> verify SLO holds -> reopen safely -> POSTMORTEM (§6)
```

## 4. Kill-switch procedure

_The halt is the most important control in this document. It must be one action, known cold, and authorized in advance - rehearse it before you need it._

| Step | Action |
|---|---|
| 1 | **Halt:** {{the exact command / dashboard toggle / feature flag that stops the agent}} |
| 2 | **Verify:** confirm no new tasks start and in-flight tasks drain or abort safely |
| 3 | **Revoke:** pull the agent's tokens / disable its MCP servers if exfil suspected ([`mcp-server-governance.md`](./mcp-server-governance.md)) |
| 4 | **Snapshot:** preserve traces/logs/config at time of halt for the postmortem |
| 5 | **Announce:** post that the agent is halted and who did it |

**Authorized to pull the kill switch:** {{on-call engineer, incident lead, CPTO}} - _no approval needed for Sev-1; act first, explain after._

_Test this path on a schedule. A kill switch you have never pulled is a hope, not a control._

## 5. Comms templates

_Communicate early and plainly. Silence during an agent incident reads as loss of control._

**Internal (incident channel):**
> {{SEV-n}} on **{{agent}}** since {{time}}. Impact: {{what/who}}. Status: {{contained / mitigating}}. Action taken: {{kill-switch / rollback / HITL raised}}. Next update: {{time}}. Lead: {{name}}.

**Stakeholder / leadership:**
> We detected {{issue}} affecting {{scope}} at {{time}}. The agent is {{halted / running with reduced autonomy}}. No further {{harm / exposure}} since {{time}}. Root-cause and a postmortem follow by {{date}}.

**Customer-facing (if external impact):**
> We identified an issue affecting {{feature}} between {{start}} and {{end}}. It is resolved / mitigated. {{What we are doing}}. We will share findings by {{date}}.

## 6. Containment checklist (step-by-step)

_Tick in order during a live incident. Designed to be followed under pressure._

- [ ] Declare severity and assign an incident lead.
- [ ] **Contain:** hit the kill switch, or throttle / drop the agent to suggest-only.
- [ ] Stop the specific harm: disable offending tool / MCP server; cap spend; block egress if exfil suspected.
- [ ] Snapshot traces, logs, and the exact config/model version in play.
- [ ] **Diagnose:** identify the last change (deploy, prompt, model, data) and the blast radius.
- [ ] **Mitigate:** roll back to last-good config, or raise HITL, or tighten the guardrail.
- [ ] Verify the trigger has cleared and SLOs are recovering.
- [ ] **Communicate** per §5 at each checkpoint.
- [ ] Decide reopen criteria; reopen only when the SLO holds over a defined window.
- [ ] Open the postmortem and assign an owner.

## 7. Handoff to postmortem

_Every Sev-1 and Sev-2 gets a blameless postmortem. The incident is not closed until the writeup and its action items exist._

| Field | Value |
|---|---|
| Incident ID / severity | {{}} |
| Detected at / resolved at | {{}} / {{}} |
| Trigger | {{}} |
| Root cause (preliminary) | {{}} |
| Customer/data impact | {{}} |
| Postmortem owner | {{}} |
| Postmortem due | {{date}} |

Complete the writeup in [`postmortem-template.md`](./postmortem-template.md). Track action items to closure - an incident with no shipped fix will recur.

## 8. Severity quick-reference

| Sev | Page? | Kill switch authorized | Postmortem |
|---|---|---|---|
| Sev-1 | Yes, immediate | Yes - act first | Required |
| Sev-2 | Yes | Yes | Required |
| Sev-3 | No | Owner discretion | Optional |
