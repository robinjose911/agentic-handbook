# Production Readiness Checklist

**Purpose:** A go / no-go gate a CPTO can sign before an agent touches production traffic. Each gate is
a hard stop: any "no" blocks launch until it is a "yes" or an accepted, owned exception.
**When to use:** Before first production launch, and again before any autonomy-tier promotion.
**How to fill:** Copy this file, work each gate with the named owner, and record `PASS` / `FAIL` /
`WAIVED (owner, expiry)`. Delete the _italic guidance_. Do not launch with an unwaived FAIL.

---

## How to use this gate

Every gate below has an **owner** and a **decision**. The launch decision is the AND of all gates: one
unwaived FAIL = no-go. A WAIVED gate needs a named owner, a reason, and an expiry date — waivers are
debt, not exemptions.

| Agent | {{name}} | Capability tier | {{L0–L3, per `capability-tier-ladder.md`}} |
|-------|----------|-----------------|--------------------------------------------|
| Launch owner | {{name}} | Target date | {{date}} |

## 1. Security

- [ ] Threat model done and current (link [`prompt-injection-threat-model.md`](prompt-injection-threat-model.md)).
- [ ] Lethal-trifecta check: no single surface has private-data access **and** untrusted input **and** external egress, or a leg is provably broken.
- [ ] Tool tokens are least-privilege and scoped; no shared god-credentials.
- [ ] Write/spend/send tools gated behind approval per the HITL policy.
- [ ] MCP servers (if any) pass [`mcp-server-governance.md`](mcp-server-governance.md) intake.

## 2. Privacy & data

- [ ] Data the agent can read is inventoried and minimized; no unnecessary PII in context.
- [ ] Payloads logged by reference, not raw, where they contain sensitive data.
- [ ] Retention + deletion policy defined for traces and audit logs.
- [ ] Data-processing basis is documented (consent / contract / legitimate interest).

## 3. Cost

- [ ] Hard per-task cost cap enforced **pre-execution** (not just alerted after).
- [ ] Budget/loop caps prevent runaway loops (max steps, max tokens, max wall-clock).
- [ ] Cost-per-task SLO defined and dashboarded (link [`agent-slo-definition.md`](agent-slo-definition.md)).
- [ ] ROI hypothesis still holds at expected volume (link [`roi-framework.md`](roi-framework.md)).

## 4. Reliability

- [ ] Idempotency + retries on side-effecting tools; no double-spend / double-send on retry.
- [ ] Timeouts and circuit breakers on every external call.
- [ ] Graceful degradation + fallback defined for each failure mode.
- [ ] Load/soak tested at expected peak.

## 5. Rollback

- [ ] One-command rollback to the previous known-good version, tested.
- [ ] Kill switch halts the agent in flight; authorized operators named.
- [ ] Feature-flag / canary path to ramp traffic and pull back fast.
- [ ] Rollback does not corrupt in-flight state (compensating actions defined).

## 6. Monitoring & observability

- [ ] Lifecycle traces emitted (OpenTelemetry GenAI spans) for every run.
- [ ] Dashboards for success rate, latency, tool errors, escalation rate, cost.
- [ ] Alerts wired to on-call with thresholds tied to the SLOs.
- [ ] Drift / regression detection on the key quality metric.

## 7. Evaluations

- [ ] Eval set exists with a labeled golden dataset (link [`eval-plan-template.md`](eval-plan-template.md)).
- [ ] Launch gate metric + threshold defined and currently passing with margin.
- [ ] Evals run automatically on every change; a regression blocks merge.
- [ ] LLM-as-judge (if used) is itself validated, with known failure modes documented.

## 8. Incident response

- [ ] Escalation runbook exists and on-call is staffed (link [`escalation-runbook.md`](escalation-runbook.md)).
- [ ] Severity levels + comms templates defined.
- [ ] Postmortem process agreed (link [`postmortem-template.md`](postmortem-template.md)).
- [ ] Audit log is immutable and sufficient to reconstruct any decision.

## 9. EU AI Act & compliance

- [ ] Risk class assigned per [`capability-tier-ladder.md`](capability-tier-ladder.md) and the domain (chapter 12).
- [ ] If high-risk: technical documentation (Art. 11), automatic logging (Art. 12), and human oversight (Art. 14) are wired into the architecture, not bolted on.
- [ ] Transparency obligations met (users told they are interacting with / affected by an AI system where required).
- [ ] DPIA / risk assessment filed where required; legal sign-off recorded.

## Launch decision

| Gate | Owner | Decision (PASS / FAIL / WAIVED) | Notes |
|------|-------|---------------------------------|-------|
| Security | {{}} | {{}} | {{}} |
| Privacy & data | {{}} | {{}} | {{}} |
| Cost | {{}} | {{}} | {{}} |
| Reliability | {{}} | {{}} | {{}} |
| Rollback | {{}} | {{}} | {{}} |
| Monitoring | {{}} | {{}} | {{}} |
| Evaluations | {{}} | {{}} | {{}} |
| Incident response | {{}} | {{}} | {{}} |
| EU AI Act | {{}} | {{}} | {{}} |

**Go / No-go:** {{decision}} — **signed:** {{name, role, date}}
