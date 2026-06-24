# 10 · Agent identity & auth

This is the **I** in AGENTIC — Identity — and it is the surface teams skip until it bites them in
production. The demo works because the agent runs as you: it borrows your session, your cookies, your
god-mode service account, and it can touch everything you can. That is fine on a laptop and a
liability everywhere else. The moment an agent acts on behalf of users, calls third-party tools, and
runs unattended, "who is this agent and what is it allowed to do" stops being a footnote and becomes
the control that decides your blast radius. An agent is a new kind of principal — autonomous, fast,
and occasionally wrong — and it needs a first-class identity, not a borrowed one.

## Why identity gets skipped, and why that's the bug

Identity gets skipped for the same reason it always does: it is invisible when it works and the demo
doesn't need it. Standing up OAuth flows, minting scoped tokens, and wiring least-privilege roles is
unglamorous plumbing that produces no visible feature. So the agent ships with a long-lived API key in
an environment variable, or a service account with broad write access, or — worst of all — the user's
own credentials passed straight through.

The bill comes due in production for three reasons. First, **autonomy multiplies a credential's
reach**: a human with broad access makes a handful of considered actions an hour; a compromised or
confused agent makes thousands in a minute. Second, agents are **uniquely exploitable** — prompt
injection (see [chapter 11](11-security-and-threat-model.md)) can turn an agent's own credentials
against you, so the question is never just "is the key leaked" but "what can a hijacked-but-legitimate
agent do with the access it *legitimately* holds." Third, **auditability collapses** when everything
runs as one shared identity: you cannot tell which agent, which user, or which task performed an
action, which makes incident response and compliance guesswork. Least privilege is not hardening you
add later; for agents it is the difference between a contained incident and an open-ended one.

## The building blocks

The good news is the standards have caught up, and you should adopt them rather than invent your own.

**OAuth 2.1 as the baseline.** OAuth 2.1 consolidates the modern, secure subset of OAuth — mandatory
PKCE, no implicit flow, no password grant — and it is the right foundation for agent auth. Agents
should obtain access through proper authorization flows, not by hoarding static secrets. This matters
because it gives you tokens that are *scoped*, *short-lived*, and *revocable* — three properties a
long-lived API key lacks entirely.

**Scoped credentials and capability tokens.** The unit of access should be the *capability*, not the
account. A token that grants exactly "read calendar for user U until 4pm" is a capability token: narrow
in scope, narrow in audience, narrow in time. Compare that to a service account that can do anything to
anyone forever — the capability token turns a leak into a small, time-boxed, attributable problem. Mint
tokens per task and per user where you can; the cost is a little plumbing and the payoff is a blast
radius measured in minutes and rows rather than systems.

**The MCP authorization spec.** When your agent talks to tools over the Model Context Protocol, lean on
its authorization model rather than rolling your own. The
[MCP specification](../references.md#mcp-spec) defines an OAuth 2.1-based authorization framework for
how MCP clients obtain and present tokens to MCP servers — treating the server as a resource server and
delegating identity to a proper authorization server. If your tool layer is MCP (see
[chapter 06](06-protocol-stack-skills-mcp-a2a.md) for the protocol stack), this is where agent
identity and tool access meet, and it is worth implementing to spec instead of stapling bearer tokens
onto requests.

**Client ID Metadata Documents and Cross-App Access.** Two emerging patterns reduce the registration
and consent friction that otherwise pushes teams toward shared credentials. *Client ID Metadata
Documents* let a client be identified by a URL that hosts its metadata, so dynamically-spawned agents
can present a verifiable identity without a manual pre-registration step per agent — useful when you
spin up many short-lived agents. *Cross-App Access* patterns let an agent acting in one application
obtain scoped access to another on the user's behalf through proper delegation, rather than asking the
user to paste credentials or copy a token between apps. Both push you toward the same destination:
verifiable, delegated, scoped identity instead of static shared secrets.

## Least privilege, in practice

The anti-pattern to name and kill is **the one god service account** — a single identity with broad
permissions that every agent and every task shares. It is convenient, it makes the demo easy, and it
turns any single compromise into total compromise while making your audit log useless. Do not ship it.

Build the opposite by default:

- **One identity per agent role, not per fleet.** The triage agent, the refund agent, and the research
  agent are different principals with different permission sets. When one misbehaves you can revoke or
  constrain it without taking down the others, and your logs say *which* agent acted.
- **Scope to the task, mint just-in-time.** Prefer short-lived, narrowly-scoped tokens minted for the
  current task over standing grants. An agent that needs to read one calendar should hold a token that
  reads one calendar, expiring soon, not a permanent calendar-admin role.
- **Delegate user authority explicitly.** When the agent acts for a user, carry that user's identity
  through the chain (via proper on-behalf-of delegation) so downstream systems enforce *that user's*
  permissions, not the agent's superset. This keeps row-level and tenant-level access controls intact
  and keeps the audit trail honest.
- **Make tool access mirror identity.** The contracts in [chapter 04](04-tool-design-and-contracts.md)
  should be enforced by the token, not just the prompt: a worker that only summarizes should hold no
  token that can write. Identity and tool design are two halves of the same control — a narrow tool
  surface is only as safe as the credential behind it.
- **Log the principal on every action.** Every tool call should record which agent identity, on behalf
  of which user, performed it. Without that, you have no incident response and no compliance story.

None of this is exotic; it is the same least-privilege, scoped-credential discipline that secures human
and service access, applied to a faster, more autonomous, more easily-hijacked principal. Agents raise
the stakes — they act at machine speed, they can be turned against you through their inputs, and they
multiply across your stack — so the discount you take by skipping identity is borrowed against a much
larger incident. Build the identity surface as deliberately as you build the agent, before it ships,
not after the postmortem.
