# 06 · Protocol stack: Skills, MCP, A2A

This is the **N** (Networks) surface of AGENTIC: the protocols that connect an agent to its tools, its
expertise, and other agents. Three standards dominate the conversation, and they are constantly
conflated. They are not competitors; they sit at different layers and answer different questions. Get
the mental model right and most "which protocol?" arguments dissolve.

- **MCP is connectivity** — *agent-to-tool*. The
  [Model Context Protocol](../references.md#mcp-spec) standardizes how an agent discovers and calls
  external tools, resources, and data sources. It is the USB-C port: one wire format so any client can
  talk to any server. Use it when the question is *"how does my agent reach this system?"*
- **Skills are expertise** — *packaged know-how*. The
  [Agent Skills standard](../references.md#agent-skills-standard) bundles instructions, scripts, and
  resources the agent loads on demand to perform a task well. Skills do not move data between processes;
  they tell the agent *how* to do something. Use them when the question is *"how does my agent do this
  competently?"*
- **A2A is coordination** — *agent-to-agent*. The
  [A2A protocol](../references.md#a2a-spec) standardizes how independent agents — possibly built by
  different teams on different stacks — discover each other (via Agent Cards), delegate tasks, and
  exchange results. Use it when the question is *"how do my agents talk to each other?"*

![The protocol stack: MCP connects to tools, A2A coordinates agents](../assets/diagrams/11-mcp-vs-a2a-stack.png)

## When to use each — and when none

The honest default is **none of them.** A single agent calling a handful of in-process functions needs
no protocol at all — direct function calls are simpler, faster, and have a smaller attack surface.
Reach for a protocol only when its specific benefit pays for its cost.

- **Reach for MCP** when you want to reuse an existing, governed connector (filesystem, GitHub, a
  database) instead of writing and maintaining bespoke tool glue, or when third parties will plug tools
  into your agent. The [reference servers](../references.md#mcp-servers) and the
  [awesome-mcp-servers index](../references.md#awesome-mcp-servers) show the breadth. The cost is a new,
  third-party trust boundary inside your agent — see §3.
- **Reach for Skills** when the *capability* is the reusable unit — a domain procedure you want
  versioned and shared across agents — rather than a connection. Skills compose *with* MCP: a Skill can
  describe how to use an MCP-connected tool well.
- **Reach for A2A** only for genuine multi-agent coordination across organizational or runtime
  boundaries, and only after [chapter 02](02-decision-framework.md) has convinced you that multi-agent
  is the right shape at all. Most "multi-agent" systems are one process and need no wire protocol
  between roles. A2A's cost is a coordination layer with its own failure modes.

A useful rule of thumb: **MCP and A2A are wires; Skills are knowledge.** You can run a perfectly good
production agent with Skills and direct tool calls and zero MCP or A2A — protocols are for reach and
interoperability, not a maturity badge.

## Why MCP governance matters: a breach timeline

MCP's strength — any server can hand your agent new tools — is also its danger: every server is
third-party code with a foot inside your agent's trust boundary, and tool descriptions plus tool results
are *untrusted input* that can carry prompt injection. This is not theoretical. A short, sobering
timeline (public incidents only; figures labeled):

- **GitHub MCP prompt-injection (May 2025).** Researchers showed a malicious GitHub issue could
  hijack an agent using the GitHub MCP server, coaxing it to leak data from private repositories — a
  textbook [lethal-trifecta](../references.md#willison-lethal-trifecta) exploitation through a connected
  server.
- **mcp-remote OAuth RCE.** A flaw in the mcp-remote OAuth flow allowed remote code execution: **[CVE-2025-6514](../references.md#cve-2025-6514) — the affected package had roughly 437,000 downloads, as of June 2026 — verify before relying.** A connectivity shim became a host-takeover path.
- **Smithery supply-chain.** A compromise in the Smithery MCP registry/installer surface illustrated the
  rug-pull-via-update class: a server you vetted last month ships malicious tooling in its next release.
- **Postmark MCP impostor.** A look-alike "Postmark" MCP server impersonated the legitimate vendor to
  harvest credentials and traffic — a typosquat aimed squarely at the install step.

The lesson is not "avoid MCP"; it is "govern it like the third-party code it is." Each of these maps to a
control in the [MCP server governance template](../templates/mcp-server-governance.md): provenance and
publisher checks defeat the impostor, version+digest pinning with no auto-update defeats the supply-chain
rug-pull, tool-description diffing catches injected instructions, and egress allowlists break the
exfiltration leg. These failure classes are exactly what the
[OWASP Top 10 for Agentic Applications 2026](../references.md#owasp-agentic-top-10) catalogues —
untrusted tool surfaces, excessive agency, and supply-chain risk are first-class entries, not edge cases.

## Putting the stack to work safely

Adopt the protocols in order of trust cost. Start with Skills and direct tool calls, the lowest-risk
rung. Add MCP only behind the governance gate: no server reaches an agent until it has cleared the intake
checklist, been pinned to an exact version and digest, and been signed into the allowlist register by a
named owner — full process in the
[MCP server governance template](../templates/mcp-server-governance.md). Add A2A last, and only for
real cross-boundary coordination, treating every peer agent's output as untrusted input just as you would
a tool result.

The connective tissue across all three is the same threat discipline:
*everything that crosses a protocol boundary is untrusted until proven otherwise.* A tool description, a
Skill loaded from a registry, an A2A peer's task result — each can carry an instruction you did not
write. That is why the protocol stack and the [security threat model](11-security-and-threat-model.md)
are two views of one problem: connectivity is also exposure, and the governance is the price of the
reach.
