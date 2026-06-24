# References

Every external claim in this handbook cites a row here. Each row has a stable `id` (the `<a id>`
anchor) that chapters link to as `../references.md#<id>`. Volatile figures — star counts, benchmark
percentages, dates — carry a label: _as of June 2026 — verify before relying_. Vendor/self-reported
numbers are marked _self-reported_.

Rows above **Further reading** are claim-backing: each is cited by at least one chapter, and every
chapter citation resolves to one (the bijection, enforced by `test_references.py`). The **Further
reading** section is a curated ecosystem/format index that is intentionally not individually cited.

> Star counts and version dates below are **_as of June 2026 — verify before relying_**. They are
> approximate and move constantly; they convey relative scale, not precision.

## Tier 1 — Production playbooks & pattern catalogs

- <a id="anthropic-building-effective-agents"></a>[Anthropic, "Building Effective Agents"](https://www.anthropic.com/engineering/building-effective-agents) (December 2024) — the canonical five workflow/agent patterns. _self-reported_
- <a id="openai-practical-guide-agents"></a>[OpenAI, "A Practical Guide to Building Agents"](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf) — OpenAI's patterns + Agents SDK framing. _self-reported_
- <a id="12-factor-agents"></a>[humanlayer/12-factor-agents](https://github.com/humanlayer/12-factor-agents) — the manifesto-lane playbook (~17.8K stars _as of June 2026 — verify_).
- <a id="agent-skills-standard"></a>[anthropics/skills + agentskills.io](https://github.com/anthropics/skills) — reference implementation of the Agent Skills standard.

## Tier 2 — Multi-agent & framework references

- <a id="smolagents"></a>[HuggingFace smolagents](https://github.com/huggingface/smolagents) — CodeAct-first minimalist agents (~26.3K stars _as of June 2026 — verify_).
- <a id="browser-use"></a>[Browser Use](https://github.com/browser-use/browser-use) — browser-agent toolkit (~50K stars; raised $17M March 2025 — _self-reported, as of June 2026 — verify_).

## Tier 3 — Reliability, evaluation, observability, guardrails

- <a id="langfuse"></a>[Langfuse](https://github.com/langfuse/langfuse) — MIT-licensed LLM engineering/observability platform (~26.5K stars _as of June 2026 — verify_).
- <a id="arize-phoenix"></a>[Arize Phoenix](https://github.com/Arize-ai/phoenix) — OTel-native tracing + evals.
- <a id="deepeval"></a>[DeepEval](https://github.com/confident-ai/deepeval) — pytest-style LLM evaluation.
- <a id="ragas"></a>[Ragas](https://github.com/explodinggradients/ragas) — RAG-specific evals.
- <a id="humanlayer"></a>[HumanLayer](https://github.com/humanlayer/humanlayer) — canonical human-in-the-loop SDK.

## Tier 4 — MCP ecosystem

- <a id="mcp-servers"></a>[modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) — reference MCP servers (~85K stars _as of June 2026 — verify_).
- <a id="awesome-mcp-servers"></a>[punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) — MCP server index (~60K stars _as of June 2026 — verify_).

## Tier 6 — Authoritative essays & specs

- <a id="cognition-dont-build-multi-agents"></a>[Cognition, "Don't Build Multi-Agents"](https://cognition.ai/blog/dont-build-multi-agents) (June 12, 2025) — the single-agent argument.
- <a id="anthropic-multi-agent-research"></a>[Anthropic, "How we built our multi-agent research system"](https://www.anthropic.com/engineering/built-multi-agent-research-system) (June 13, 2025) — orchestrator-worker case study. _self-reported_
- <a id="cognition-multi-agents-working"></a>[Cognition, "Multi-Agents: What's Actually Working"](https://cognition.ai/blog/multi-agents-working) (April 22, 2026 _— verify_) — the 2026 reconciliation.
- <a id="mast-taxonomy"></a>[Berkeley MAST taxonomy](https://arxiv.org/abs/2503.13657) (NeurIPS 2025) — 14 multi-agent failure modes across ~1,600 traces. _self-reported_
- <a id="willison-lethal-trifecta"></a>[Simon Willison, "The Lethal Trifecta"](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/) (June 16, 2025) — private data + untrusted content + external comms.
- <a id="meta-rule-of-two"></a>[Meta, "Agents Rule of Two"](https://ai.meta.com/blog/practical-ai-agent-security/) (October 31, 2025 _— verify_) — at most two of {untrusted input, sensitive data, state-change/egress}.
- <a id="owasp-agentic-top-10"></a>[OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) (released December 2025 _— verify_) — ASI01–ASI10.
- <a id="codeact"></a>[Wang et al., "Executable Code Actions (CodeAct)"](https://arxiv.org/abs/2402.01030) (ICML 2024) — +20% success, ~30% fewer steps vs JSON tool calls. _self-reported_
- <a id="mcp-spec"></a>[Model Context Protocol specification](https://modelcontextprotocol.io/specification) (2025-06-18 OAuth; 2025-11-25 enterprise auth _— verify_) — agent-to-tool connectivity.
- <a id="a2a-spec"></a>[A2A specification](https://a2a-protocol.org) (Linux Foundation, June 23, 2025 _— verify_) — agent-to-agent coordination.
- <a id="otel-genai"></a>[OpenTelemetry GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/) (v1.40, April 2026 _— verify_) — lifecycle spans + token/cost metrics.
- <a id="eu-ai-act"></a>[EU AI Act (Regulation 2024/1689)](https://artificialintelligenceact.eu/) — risk classes + Articles 11/12/14. _verify current guidance_
- <a id="metr-horizon"></a>[METR, "Measuring AI task-completion time horizons"](https://metr.org/blog/) — the time-horizon metric (a frontier model at a ~14.5-hr 50% horizon, February 2026 — _self-reported, as of June 2026 — verify_).
- <a id="tau-bench"></a>[τ-bench](https://github.com/sierra-research/tau-bench) — tool-agent benchmark (an empty-response agent scores ~38% on τ-bench-Airline — _self-reported caveat, verify_).
- <a id="swe-bench"></a>[SWE-bench](https://www.swebench.com/) — software-engineering agent benchmark (Verified / Multimodal / Pro).
- <a id="routellm"></a>[RouteLLM](https://github.com/lm-sys/RouteLLM) — model routing (up to ~85% cost reduction at ~95% quality on benchmark workloads — _self-reported, verify_).

## Tier 7 — Named incidents

- <a id="cve-2025-6514"></a>[CVE-2025-6514 — mcp-remote OAuth proxy RCE](https://nvd.nist.gov/vuln/detail/CVE-2025-6514) — the affected package saw ~437,000 downloads _as of June 2026 — verify_.
- <a id="cve-2025-8217"></a>[CVE-2025-8217 — Amazon Q wiper backdoor](https://nvd.nist.gov/vuln/detail/CVE-2025-8217) — injected destructive instruction _as of June 2026 — verify_.
- <a id="agent-incidents"></a>[Agent security incident roundup](https://simonwillison.net/tags/prompt-injection/) — Replit prod-db deletion, Microsoft 365 Copilot EchoLeak, the ~$47K multi-agent loop, and related cases — _as of June 2026 — verify each against primary sources_.

## Further reading

Ecosystem, cookbook, and format-inspiration references — a curated index, not individually cited.

- <a id="anthropic-cookbook"></a>[anthropics/anthropic-cookbook](https://github.com/anthropics/anthropic-cookbook) — official `patterns/agents/` reference implementations (~32.9K stars _as of June 2026 — verify_).
- <a id="openai-cookbook"></a>[openai/openai-cookbook](https://github.com/openai/openai-cookbook) — canonical OpenAI patterns (~70K stars _as of June 2026 — verify_).
- <a id="crewai"></a>[CrewAI](https://github.com/crewAIInc/crewAI) — role-based multi-agent framework (~50.8K stars _as of June 2026 — verify_).
- <a id="langgraph"></a>[LangGraph](https://github.com/langchain-ai/langgraph) — graph/checkpointer agent runtime with supervisor + swarm libraries.
- <a id="pydantic-ai"></a>[pydantic/pydantic-ai](https://github.com/pydantic/pydantic-ai) — type-safe Python agents (~16K stars _as of June 2026 — verify_).
- <a id="vercel-ai-sdk"></a>[Vercel AI SDK](https://github.com/vercel/ai) — TypeScript agent/LLM SDK (~17.7K stars _as of June 2026 — verify_).
- <a id="nemo-guardrails"></a>[NVIDIA NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails) — Colang-DSL guardrails.
- <a id="system-design-primer"></a>[donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer) — the gold-standard reference repo (~290K stars _as of June 2026 — verify_).
- <a id="kubernetes-the-hard-way"></a>[kelseyhightower/kubernetes-the-hard-way](https://github.com/kelseyhightower/kubernetes-the-hard-way) — sequential numbered-docs pedagogy.
- <a id="system-design-101"></a>[ByteByteGoHq/system-design-101](https://github.com/ByteByteGoHq/system-design-101) — visuals-do-the-work format.
