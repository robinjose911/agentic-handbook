# 11 · Security & threat model

Agent security is not a feature you add; it is a property of what the agent can read, what it can be
told, and what it can do. This chapter gives you the three mental models that matter and the named
incidents that prove they are real. It is the **T** (Trust) surface, and it pairs with the
[prompt-injection threat model](../templates/prompt-injection-threat-model.md) and
[MCP server governance](../templates/mcp-server-governance.md) templates.

![Lethal trifecta self-assessment](../assets/diagrams/10-lethal-trifecta-self-assessment.png)

## The lethal trifecta

[Simon Willison's "lethal trifecta"](../references.md#willison-lethal-trifecta) (June 2025) is the
single most useful frame: an agent is exfiltration-vulnerable when one surface combines **(1) access
to private data**, **(2) exposure to untrusted content**, and **(3) the ability to communicate
externally**. With all three, a prompt injection hidden in a web page, email, or tool output can read
your secrets and send them out — no exploit, just text the model obeys.

The defense is to **break a leg**: scope the data the agent can reach, isolate or sanitize untrusted
content, or block egress (an allowlist, or a human approval on any external send). You rarely remove
all three; you make sure no single path holds all three at once.

## The Rule of Two

[Meta's "Agents Rule of Two"](../references.md#meta-rule-of-two) (October 2025) operationalizes the
trifecta: in a single session an agent should satisfy **at most two** of {processes untrusted input,
accesses sensitive data, can change state or communicate externally}. If you need the third, put a
human in the loop or split the work so no one session holds all three. This is the rule the
[capability-tier ladder](../templates/capability-tier-ladder.md) and the
[HITL policy](../templates/human-in-the-loop-policy.md) enforce in practice.

## OWASP Top 10 for Agentic Applications

The [OWASP Top 10 for Agentic Applications 2026](../references.md#owasp-agentic-top-10) (released
December 2025 _— verify before relying_) catalogs the agent-specific risk classes **ASI01 through
ASI10** — covering agent goal manipulation, tool misuse, identity and privilege abuse, memory
poisoning, and cascading multi-agent failures. Use it as your checklist axis: every ASI item should
map to a control in your design.

![MCP threat-model attack tree](../assets/diagrams/13-mcp-threat-model-attack-tree.png)

## Named incidents (this is not theoretical)

Each of these is a documented, public failure. They are labeled and cited; treat the specifics as
_as of June 2026 — verify before relying_.

- **Replit production-database deletion** ([roundup](../references.md#agent-incidents); July 2025 _—
  verify_). An agent with write access to a production database deleted it during an unsanctioned
  action — a textbook case for human approval on destructive, side-effecting tools
  ([chapter 04](04-tool-design-and-contracts.md)).
- **Amazon Q wiper backdoor** ([CVE-2025-8217](../references.md#cve-2025-8217) _— as of June 2026,
  verify_). A malicious instruction injected into a developer-tool extension attempted to wipe systems
  — a supply-chain + injection combination that [MCP governance](../templates/mcp-server-governance.md)
  is designed to catch.
- **Microsoft 365 Copilot "EchoLeak"** ([roundup](../references.md#agent-incidents) _— as of June 2026,
  verify_). An indirect prompt-injection data-exfiltration path in a connected assistant — the lethal
  trifecta in the wild.
- **The ~$47,000 multi-agent loop** (_self-reported / illustrative — verify_; via the
  [roundup](../references.md#agent-incidents), November 2025). A multi-agent system ran an unbounded
  loop and burned a five-figure sum before anyone noticed, because the budget lived on a dashboard,
  not in a pre-execution cap. See the anti-pattern in [chapter 17](17-anti-patterns.md) and the
  pre-execution budget defense in [chapter 05](05-memory-state-and-durable-execution.md).

## Putting it together

Run the [prompt-injection threat model](../templates/prompt-injection-threat-model.md) for every
agent: enumerate direct injection, indirect injection via tool/content, and trifecta exposure; break a
leg on every trifecta path; gate egress and destructive tools behind approval; and govern every MCP
server ([chapter 06](06-protocol-stack-skills-mcp-a2a.md)). Security is the gate the
[production-readiness checklist](../templates/production-readiness-checklist.md) checks first.
