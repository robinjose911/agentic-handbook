# Tool Contract

**Purpose:** Specify exactly one tool an agent may call — its inputs, outputs, side effects, and blast radius — so the model's freedom ends where your guardrails begin.
**When to use:** Before you expose any tool to an agent, and again whenever the tool gains a write, a spend, or a new permission scope.
**How to fill:** Copy this file into your repo (one per tool), replace every `{{PLACEHOLDER}}`, and delete the _italic guidance_.

---

## 1. Identity

| Field | Value |
|-------|-------|
| Tool name | `{{exact_callable_name}}` |
| One-line purpose | {{what it does, in plain language}} |
| Owner | {{team / person responsible for this tool}} |
| Version | {{semver or date}} — _as of {{month year}} — verify before relying_ |
| Backing system | {{the API / DB / service this wraps}} |

_The name the model sees is part of the prompt. Name it for what it does, not for the system behind it (`refund_order`, not `call_billing_v2`)._

## 2. When to call / when NOT to call

- **Call when:** {{the specific condition that makes this the right tool}}
- **Do NOT call when:** {{cases the model gets wrong — overlapping tools, missing prerequisites, ambiguous intent}}
- **Preconditions:** {{state that must already be true, e.g. order exists, user is authenticated}}

_This text often lives verbatim in the tool description. Be concrete about the failure: "Do not call to look up an order — use `get_order` for that; this tool mutates."_

## 3. Input schema

| Param | Type | Required | Validation / constraint |
|-------|------|----------|-------------------------|
| `{{param}}` | {{string / int / enum / object}} | {{yes / no}} | {{regex, range, allowed values, max length}} |
| `{{param}}` | {{type}} | {{yes / no}} | {{constraint}} |

_Validate at the boundary, not in the prompt. The model will pass malformed and out-of-range values; reject them before the side effect, never after._

## 4. Output schema

| Field | Type | Meaning |
|-------|------|---------|
| `{{field}}` | {{type}} | {{what it represents}} |
| `status` | enum | `ok` / `rejected` / `error` |

- **On success returns:** {{the shape and size — cap large payloads so they don't blow the context}}
- **What the agent does with the output:** {{how the result feeds the next step}}

## 5. Side effects & idempotency

| Field | Value |
|-------|-------|
| Classification | {{read-only / writes-data / spends-money / sends-message / external-irreversible}} |
| Reversible? | {{yes — how / no}} |
| Idempotent? | {{yes / no}} |
| Idempotency key | {{the key that dedupes a retry, or "none — retries double-act"}} |

_A read-only tool is cheap to get wrong. A tool that sends, spends, or deletes is not — those need section 7 and 8 filled with care. If the tool is not idempotent, retries are a correctness bug, not a convenience._

## 6. Error modes & agent response

| Error | Meaning | What the agent should do |
|-------|---------|--------------------------|
| `{{invalid_input}}` | {{validation failed}} | {{do not retry; re-plan or ask the user}} |
| `{{not_found}}` | {{target does not exist}} | {{stop; surface to user, do not invent}} |
| `{{rate_limited}}` | {{quota exceeded}} | {{back off per section 7, then retry once}} |
| `{{upstream_5xx}}` | {{backing system down}} | {{retry with backoff; after N, escalate}} |
| `{{forbidden}}` | {{out of permission scope}} | {{stop; never retry; flag for review}} |

_Never let the agent paper over an error by hallucinating success. A `not_found` is an answer, not a prompt to guess._

## 7. Rate, cost & budget limits

- **Rate limit:** {{calls per minute / per task / per user}}
- **Cost per call:** {{$ or token cost, if any}} — _self-reported / illustrative_
- **Per-task cap:** {{hard ceiling enforced pre-call, not after}}
- **On limit hit:** {{queue / reject / escalate}}

## 8. Auth, permissions & approval (least privilege)

| Field | Value |
|-------|-------|
| Auth method | {{scoped token / workload identity / per-user OBO}} |
| Permission scope | {{the narrowest scope that works — e.g. `refunds:create` only}} |
| Acts as | {{the agent's own identity / the end user — never a shared admin}} |
| Capability tier | {{L0–L4, see `capability-tier-ladder.md`}} |
| Human approval required? | {{auto / human-approve / two-person — see `human-in-the-loop-policy.md`}} |

_Least privilege is the whole game. A tool scoped to `refunds:create` cannot be tricked into `refunds:delete`. If this tool both reads untrusted content and can take a consequential external action, you are one prompt-injection away from the lethal trifecta — gate it with HITL._

## 9. Observability

_Every call emits a structured log line. List what is captured._

- **Logged on every call:** {{tool name, args (redacted), caller identity, decision, latency, cost, result status}}
- **Redaction:** {{which fields are masked — PII, secrets, tokens}}
- **Correlation:** {{the trace/span id that ties this call to the agent run}}
- **Alert on:** {{repeated rejections, cost spikes, scope-violation attempts}}

## 10. Worked examples

| Intent | Call | Side effect | Expected result |
|--------|------|-------------|-----------------|
| Refund a valid order | `refund_order(order_id="A-1042", amount=29.00, reason="duplicate")` | spends-money, irreversible | `{status: ok, refund_id: "R-88"}` |
| Refund above policy cap | `refund_order(order_id="A-1042", amount=5000.00, reason="goodwill")` | none — rejected pre-call | `{status: rejected, error: "exceeds_auto_refund_cap"}` → agent escalates to human-approve |

_Keep at least one happy path and one rejection. The rejection row is the one that proves your boundary actually holds._
