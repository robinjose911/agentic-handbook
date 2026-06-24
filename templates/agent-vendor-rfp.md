# Agent Vendor RFP

**Purpose:** A vendor-neutral request-for-proposal questionnaire for evaluating any agentic-AI product
or platform. The answers (and the ones a vendor dodges) tell you whether you can run their agent in
production and get out later.
**When to use:** When evaluating a build-vs-buy decision toward "buy" (pair with
[`build-vs-buy-harness.md`](build-vs-buy-harness.md)), or comparing agent platforms head-to-head.
**How to fill:** Send sections 1–9 to each vendor. Score answers in
[`build-vs-buy-harness.md`](build-vs-buy-harness.md). Treat "we can't share that" on security or
data-handling questions as a scored answer, not a blank.

---

## 1. Company & product

1. What exactly does the product do, and where does an agent's autonomy end and a human's begin?
2. How long has the product been in production with paying customers, and at what scale (_ask for a reference, not a logo wall_)?
3. What is your roadmap for the next 12 months, and what has been deprecated in the last 12?
4. What is your funding / commercial stability, and what happens to our deployment if you are acquired or shut down?

## 2. Architecture & autonomy

5. Which capability tier (L0–L4, see [`capability-tier-ladder.md`](capability-tier-ladder.md)) does the product operate at by default, and what is the maximum it allows?
6. Can we cap autonomy, require human approval on specific actions, and enforce hard pre-execution limits?
7. What models does it use, can we bring our own, and how are we insulated from a model deprecation?
8. How does the agent decide when to stop, escalate, or hand off to a human?

## 3. Tools, integrations & MCP

9. How are tools/integrations defined, and can we add our own with our own auth?
10. Do you support the Model Context Protocol (MCP) or similar, and how are third-party servers vetted?
11. How are tool credentials scoped — least privilege per tool, or shared?
12. Can side-effecting actions (writes, spend, sends) be individually gated behind approval?

## 4. Security

13. How do you defend against direct and indirect prompt injection, and what is your stance on the lethal trifecta?
14. Have you had a third-party penetration test or audit (SOC 2 / ISO 27001), and can we see the report or summary?
15. How is data isolated between tenants, and is our data ever used to train shared models?
16. What is your vulnerability disclosure and patch SLA, and have you had a disclosed incident?
17. How are secrets and tokens stored, rotated, and revoked?

## 5. Data, privacy & residency

18. What data does the product collect, retain, and for how long, and can we configure deletion?
19. Where (which regions) is data processed and stored, and can we pin residency?
20. Are you a processor or controller for our data, and what is in your DPA?
21. Can we log payloads by reference rather than storing raw sensitive content?

## 6. Reliability & operations

22. What are your published uptime SLAs, and what credits apply when they are missed?
23. How do retries, idempotency, and rate limits work for side-effecting actions?
24. What are p50/p95 latencies at our expected volume, and how do they degrade under load?
25. How do we roll back a bad release, and is there a kill switch we control?

## 7. Evaluation & quality

26. How do you measure agent quality, and will you run our eval set against the product pre-purchase?
27. How do you detect and communicate quality regressions and model drift?
28. What observability do we get — traces, per-step logs, cost attribution — and in what format (e.g. OpenTelemetry)?
29. What is the measured task-success rate on a workload like ours (_self-reported figures are illustrative — verify_)?

## 8. Cost & commercials

30. How is pricing structured (per token / per task / per seat), and how does it scale with volume?
31. What is the realistic all-in cost at 1x and 3x our expected volume?
32. What are the exit costs — data export format, migration support, and contract notice period?
33. Is there lock-in via proprietary formats, and how hard is it to switch to a competitor?

## 9. Compliance & EU AI Act

34. How does the product help us meet EU AI Act obligations (Art. 11 technical docs, Art. 12 logging, Art. 14 human oversight) for high-risk use?
35. Do you provide the documentation and logs we need for our own conformity assessment?
36. What certifications, attestations, or regulatory engagements can you evidence (_as of {{month year}} — verify currency_)?

## Scoring

_Carry each answer into [`build-vs-buy-harness.md`](build-vs-buy-harness.md). A non-answer on sections
4, 5, or 9 should weigh heavily against the vendor._
