# MCP Server Governance

**Purpose:** Adopt and operate Model Context Protocol (MCP) servers without handing an attacker your tools - every server is third-party code with a foot inside your agent's trust boundary.
**When to use:** Before connecting any MCP server to an agent, on every version bump, and at each scheduled allowlist review.
**How to fill:** Copy this file into your repo, replace every `{{PLACEHOLDER}}`, and delete the _italic guidance_.

---

## 1. Threat framing (read first)

An MCP server gives an agent new tools - and new ways to be turned against you. The danger is the **lethal trifecta**: an agent that (1) can access private/sensitive data, (2) is exposed to untrusted content, and (3) can communicate externally (exfiltrate). Any single MCP server, or a combination, that closes all three legs is a data-exfiltration path. Tool descriptions and tool results are untrusted input and can carry prompt injection.

> **Rule:** No MCP server is approved until it has cleared the intake checklist below and an owner has signed it into the allowlist register. Pair this policy with [`prompt-injection-threat-model.md`](./prompt-injection-threat-model.md).

## 2. Intake checklist (per new server)

_Complete one of these for every server before it touches an agent. A "no" or "unknown" on a security row blocks adoption until resolved._

**Server:** {{name}} - **Reviewer:** {{name}} - **Date:** {{month year}}

| # | Check | Finding | Pass? |
|---|---|---|---|
| 1 | **Provenance / publisher** - who maintains it, reputation, repo activity | {{}} | {{Y/N}} |
| 2 | **Pinned version** - exact version/digest, no `latest` tag | {{version + digest}} | {{Y/N}} |
| 3 | **Permissions / scopes requested** - list every scope and why | {{}} | {{Y/N}} |
| 4 | **Data it can read** - what sensitive data is in reach | {{}} | {{Y/N}} |
| 5 | **Actions it can take** - every write/side-effecting tool | {{}} | {{Y/N}} |
| 6 | **Tool-description review** - read each description for injected instructions ("ignore previous", hidden directives, unicode tricks) | {{}} | {{Y/N}} |
| 7 | **Tool-result handling** - are returned results treated as untrusted? | {{}} | {{Y/N}} |
| 8 | **Sandboxing** - runs isolated (container/network policy), not on a privileged host | {{}} | {{Y/N}} |
| 9 | **Egress** - what external endpoints can it reach | {{}} | {{Y/N}} |
| 10 | **Lethal-trifecta check** - does this server (alone or combined with others on the same agent) give data access + untrusted input + external comms? | {{}} | {{Y/N}} |
| 11 | **Auth model** - token type, scope, rotation, revocation | {{}} | {{Y/N}} |
| 12 | **Update mechanism** - can it auto-update? (it must not - see §4) | {{}} | {{Y/N}} |

_If row 10 is "yes," you must break one leg of the trifecta before approval: drop the sensitive scope, isolate from untrusted input, or remove external egress. Do not approve "we'll watch it closely."_

## 3. Allowlist register

_The single source of truth for which MCP servers are approved, at what version, with what scopes, owned by whom. If it is not in this table, an agent may not connect to it._

| Server | Version / digest | Scopes granted | Read access | Write tools | Owner | Approved | Next review |
|---|---|---|---|---|---|---|---|
| {{name}} | {{x.y.z @ sha256:...}} | {{read:docs}} | {{kb only}} | {{none}} | {{name}} | {{date}} | {{date}} |
| {{name}} | {{}} | {{}} | {{}} | {{}} | {{}} | {{}} | {{}} |

_Review cadence: at least every {{quarter}}, and immediately on any security advisory. Stale entries past their review date are auto-suspended._

## 4. Update & supply-chain policy

_An MCP server you trusted last month can ship a malicious tool description in the next release. Treat updates as new code, not patches._

- **No auto-update.** Pin to an exact version and digest. Disable any client-side auto-upgrade.
- **Sign + review every update.** A bump re-runs the full intake checklist (§2), with special attention to changed tool descriptions and new scopes.
- **Diff tool descriptions** across versions - a new injection can hide in a one-line "improved description."
- **Source integrity.** Verify the publisher signature / digest before promotion. Prefer vendored or mirrored copies over pulling live from a public registry at runtime.
- **Two-person rule** for adding a server with any write tool or any sensitive read scope.
- **Revocation drill.** Know how to pull a server from every agent fast - see [`escalation-runbook.md`](./escalation-runbook.md).

## 5. Runtime controls

_Intake gets a server in the door safely; runtime keeps it honest. Least privilege is the whole game._

| Control | Policy |
|---|---|
| **Least-privilege tokens** | Scope tokens to the minimum the server needs; per-server, never shared; short-lived + rotated |
| **Human approval for write tools** | Any side-effecting / write / spend / external-comms tool requires explicit human confirmation per call (or per session for low-risk) |
| **Egress limits** | Allowlist outbound endpoints; deny by default; block the trifecta's exfiltration leg at the network layer |
| **Input isolation** | Do not feed untrusted/web content into an agent that also holds sensitive read scopes + external egress on the same turn |
| **Rate + spend caps** | Per-server call ceilings and budget caps; trip an alert before they bite |
| **Full audit trail** | Log every tool call, args, and result for replay; results are untrusted and logged as such |
| **Kill switch** | Per-server disable that takes effect within one task cycle |

## 6. Sign-off

_No server reaches production without a named owner and a security reviewer on record._

| Role | Name | Date |
|---|---|---|
| Requesting owner | {{name}} | {{date}} |
| Security reviewer | {{name}} | {{date}} |
| Approver (CPTO / platform lead) | {{name}} | {{date}} |

> _As of {{month year}} - verify before relying:_ MCP tool-poisoning and rug-pull-via-update remain active attack classes. Re-confirm your client enforces version pinning and surfaces tool-description changes.
