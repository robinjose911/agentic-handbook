"""Single source of the chapter + template enumerations, shared by every validator so the 19/16
contract is defined once (not retyped in test_ai_native / test_docs_structure / test_templates).
The directory-orphan tests assert the on-disk tree matches these lists in BOTH directions."""

CHAPTERS = [
    "00-introduction", "01-mnemonic-and-systems-map", "02-decision-framework", "03-pattern-catalog",
    "04-tool-design-and-contracts", "05-memory-state-and-durable-execution",
    "06-protocol-stack-skills-mcp-a2a", "07-codeact-vs-tool-calls", "08-computer-use-and-browser-agents",
    "09-model-selection-for-roles", "10-agent-identity-and-auth", "11-security-and-threat-model",
    "12-eu-ai-act-as-architecture", "13-evaluations", "14-observability-lite", "15-cost-stack",
    "16-production-readiness", "17-anti-patterns", "18-case-studies",
]

TEMPLATES_MD = [
    "agent-design-spec", "tool-contract-template", "eval-plan-template",
    "production-readiness-checklist", "human-in-the-loop-policy", "agent-risk-register",
    "postmortem-template", "capability-tier-ladder", "roi-framework", "agent-vendor-rfp",
    "build-vs-buy-harness", "mcp-server-governance", "prompt-injection-threat-model",
    "agent-slo-definition", "escalation-runbook",
]
TEMPLATES_JSON = ["observability-event-schema"]
TEMPLATES_ALL = TEMPLATES_MD + TEMPLATES_JSON  # 16
