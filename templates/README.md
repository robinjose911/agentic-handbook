# Templates

Sixteen procurement-grade, copy-paste templates — the artifacts that turn "good reading" into "we're
running this Monday." Every one is synthetic and vendor-neutral. Copy a file into your own repo,
replace the `{{PLACEHOLDER}}`s, and delete the _italic guidance_.

The capability-tier-ladder ↔ EU AI Act mapping is canonical in
[`capability-tier-ladder.md`](capability-tier-ladder.md) and must agree everywhere it appears
(enforced by `test_capability_ladder.py`).

## Design & build

| Template | What it's for |
|----------|---------------|
| [agent-design-spec](agent-design-spec.md) | Pin down what an agent is for, may do, and how you'll know it works (the **G**oals artifact). |
| [tool-contract-template](tool-contract-template.md) | Specify one tool: schema, side effects, auth scope, approval, observability. |
| [capability-tier-ladder](capability-tier-ladder.md) | The canonical L0–L4 autonomy ladder mapped to EU AI Act risk classes. |

## Evaluation & operations

| Template | What it's for |
|----------|---------------|
| [eval-plan-template](eval-plan-template.md) | The golden set, metrics, and pass gate that prove the agent works. |
| [agent-slo-definition](agent-slo-definition.md) | SLIs, SLOs, and error budgets for an agent in production. |
| [observability-event-schema.json](observability-event-schema.json) | A JSON Schema for agent lifecycle events (OTel GenAI-aligned, payload-by-reference). |
| [production-readiness-checklist](production-readiness-checklist.md) | The CPTO go/no-go gate across security, privacy, cost, reliability, rollback, monitoring, evals, incident, and EU AI Act. |

## Trust, risk & security

| Template | What it's for |
|----------|---------------|
| [human-in-the-loop-policy](human-in-the-loop-policy.md) | Which actions need human approval, by whom, with what SLA. |
| [agent-risk-register](agent-risk-register.md) | A living register of agent risks, controls, and residual ratings. |
| [prompt-injection-threat-model](prompt-injection-threat-model.md) | Direct / indirect / lethal-trifecta exposure, the attack tree, and the Rule of Two. |
| [mcp-server-governance](mcp-server-governance.md) | Intake, allowlist, and supply-chain policy for MCP servers. |

## Incident & decision-making

| Template | What it's for |
|----------|---------------|
| [escalation-runbook](escalation-runbook.md) | What to do when an agent misbehaves: contain, diagnose, mitigate, hand off. |
| [postmortem-template](postmortem-template.md) | Blameless postmortem for an agent incident. |
| [roi-framework](roi-framework.md) | Justify (or kill) an agent on the numbers. |
| [build-vs-buy-harness](build-vs-buy-harness.md) | Weighted build / buy / adopt decision, with a reversibility check. |
| [agent-vendor-rfp](agent-vendor-rfp.md) | A 36-question vendor RFP across architecture, security, data, reliability, cost, and EU AI Act. |
