# Agent Design Spec

**Purpose:** Pin down what an agent is for, what it may do, and how you will know it works — before a
line of code is written. This is the **G** (Goals) artifact in AGENTIC.
**When to use:** At the start of any new agent, and whenever you raise its autonomy tier.
**How to fill:** Copy this file into your repo, replace every `{{PLACEHOLDER}}`, and delete the
_italic guidance_. Keep it to two pages — if a section won't fit, the agent is doing too much.

---

## 1. One-line job

> {{A single sentence: "This agent <does X> for <whom> so that <outcome>."}}

## 2. Capability tier (L0–L4)

| Field | Value |
|-------|-------|
| Target tier | {{L0 / L1 / L2 / L3 — see `capability-tier-ladder.md`}} |
| EU AI Act risk class | {{minimal / limited / high-risk — must match the ladder}} |
| Why this tier | {{the consequence of a wrong action, and who absorbs it}} |

_Start one tier lower than feels comfortable. You can always promote after the evals hold._

## 3. Inputs & outputs

- **Inputs:** {{what the agent receives, and where from}}
- **Structured output contract:** {{the schema/shape it must return — link the JSON Schema or Zod/Pydantic model}}
- **Out of scope:** {{things callers might expect but this agent must refuse}}

## 4. Tools

_List every tool. Each needs a `tool-contract-template.md`. Mark side-effecting tools._

| Tool | Read / Write | Side effects | Approval (HITL?) |
|------|--------------|--------------|------------------|
| {{tool}} | {{read/write}} | {{none / sends email / spends money}} | {{auto / human-approve}} |

## 5. Autonomy & guardrails

- **Loop budget:** {{max steps / max tokens / max wall-clock per task}}
- **Cost cap:** {{hard per-task spend limit, enforced pre-execution}}
- **Stop conditions:** {{what ends the loop — success, budget, repeated failure}}
- **Kill switch:** {{how a human halts it in flight, and who can}}

## 6. Human-in-the-loop

> {{Which actions require approval, who approves, and the SLA. Link `human-in-the-loop-policy.md`.}}

## 7. Success criteria & evals

- **Definition of done:** {{the observable outcome}}
- **Eval set:** {{link the `eval-plan-template.md` — golden cases + the pass gate}}
- **Launch gate:** {{the metric + threshold that must hold before this ships}}

## 8. Failure modes & fallbacks

| Failure mode | Detection | Fallback |
|--------------|-----------|----------|
| {{e.g. tool timeout}} | {{how you notice}} | {{retry / escalate / degrade}} |

## 9. Owner & review

- **Owner:** {{name / team}}
- **Review cadence:** {{when this spec is revisited}}
- **Last reviewed:** {{date — _as of {{month year}}_}}
