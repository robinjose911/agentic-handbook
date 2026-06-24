# Agent Risk Register

**Purpose:** Keep a living, owned inventory of what can go wrong with an agent system, how likely and how bad it is, and what control brings it down to a level you can live with.
**When to use:** From the agent's design phase onward — reviewed on a cadence and after every incident, never written once and filed.
**How to fill:** Copy this file into your repo, replace every `{{PLACEHOLDER}}`, delete the _italic guidance_, and keep the seeded rows only if they apply.

---

## Scoring key

**Likelihood** and **Impact** are scored 1–5. **Rating = Likelihood × Impact** (1–25).

| Score | Likelihood | Impact |
|-------|------------|--------|
| 1 | Rare | Negligible |
| 2 | Unlikely | Minor |
| 3 | Possible | Moderate |
| 4 | Likely | Major |
| 5 | Almost certain | Severe / unrecoverable |

**Bands:** 1–6 Low · 8–12 Medium · 15–25 High. _Inherent_ = before controls. _Residual_ = after the mitigation actually lands (not when it's merely planned). A residual still in the High band needs a named owner and a date, or the agent does not ship at that tier.

## Register

| ID | Risk | Category | Likelihood | Impact | Inherent | Mitigation / control | Residual | Owner | Review |
|----|------|----------|-----------|--------|----------|----------------------|----------|-------|--------|
| R-01 | **Prompt injection** via untrusted content steers the agent into unintended tool calls | security | 4 | 5 | 20 (High) | Treat all retrieved content as untrusted; break the lethal trifecta; HITL on external actions; input/output filters | 8 (Med) | {{security}} | {{date}} |
| R-02 | **Runaway loop / cost blowout** — agent retries or recurses without bound | cost | 3 | 4 | 12 (Med) | Hard per-task step + token + $ caps enforced pre-call; loop detection; kill switch | 4 (Low) | {{platform}} | {{date}} |
| R-03 | **Tool misuse** — right tool, wrong arguments (e.g. refund 10× the amount) | reliability | 3 | 4 | 12 (Med) | Boundary validation on every tool input; spend caps; `tool-contract-template.md` per tool | 4 (Low) | {{eng owner}} | {{date}} |
| R-04 | **Data exfiltration** — private data leaves via an external-send tool | security | 3 | 5 | 15 (High) | Least-privilege scopes; egress allowlist; trifecta gate; output PII scan | 6 (Low) | {{security}} | {{date}} |
| R-05 | **Hallucinated action** — agent claims/acts as if a step succeeded that never ran | reliability | 3 | 4 | 12 (Med) | Never infer success — read back real tool results; groundedness eval; structured outputs | 4 (Low) | {{eng owner}} | {{date}} |
| R-06 | **Vendor / model outage** — provider 5xx or deprecation breaks the agent | reliability | 3 | 3 | 9 (Med) | Fallback model + degraded path; retries with backoff; status alerting; provider-neutral abstraction | 4 (Low) | {{platform}} | {{date}} |
| R-07 | **Model drift / silent behaviour change** on provider update | reliability | 3 | 4 | 12 (Med) | Pin model versions; regression evals on every change (`eval-plan-template.md`); canary before rollout | 4 (Low) | {{eng owner}} | {{date}} |
| R-08 | **Missing / tamperable audit trail** — cannot reconstruct what the agent did | compliance | 2 | 4 | 8 (Med) | Immutable structured logging of every decision + tool call + approval; trace ids; retention policy | 3 (Low) | {{compliance}} | {{date}} |
| R-09 | **Wrongful customer-facing output** — toxic, biased, or off-brand response sent | reputational | 2 | 4 | 8 (Med) | Output guardrails; HITL on first-contact sends; red-team eval slice | 4 (Low) | {{support lead}} | {{date}} |
| R-10 | **Over-broad permissions** — agent identity can do far more than its job needs | security | 3 | 4 | 12 (Med) | Least-privilege per `tool-contract-template.md`; scoped/per-user auth; periodic access review | 4 (Low) | {{security}} | {{date}} |

_Figures above are illustrative seeds, not measurements — re-score against your own system. The seed rows are a starting threat model, not a finishing one._

## How to use this register

- **Add a row** the moment a new tool, integration, or autonomy tier appears — and after every incident (`postmortem-template.md`).
- **Re-score** on the review cadence; a residual rating that has crept back up is the signal that a control has decayed.
- **High residuals** block tier promotion until the control lands and the eval proves it.
- **Cross-link** each row to its mitigating artifact: a tool contract, a HITL gate, an eval case, or a logging requirement.

## Governance

- **Register owner:** {{name / team}}
- **Review cadence:** {{monthly / quarterly}}
- **Last reviewed:** {{date — _as of {{month year}} — verify before relying_}}
