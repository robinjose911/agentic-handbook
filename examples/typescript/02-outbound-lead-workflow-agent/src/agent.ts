// The outbound-lead workflow agent. An OUTER, durable-style workflow (`runWorkflow`) iterates leads and
// owns the cross-lead aggregate; an INNER agent loop (`processLead`) runs the per-lead steps:
//
//     enrich (LLM) --> score (LLM) --> decide next action --> [HITL gate if "send outreach"]
//
// Two guardrails make this a *governed* workflow rather than a raw loop:
//   1. A pre-execution per-lead BUDGET CAP. Before every step we reserve its estimated cost; if the
//      reservation would push the lead over COST_CAP_USD, the step is REFUSED and never sent to the
//      provider — the lead stops with `budget_exhausted` (logged, not executed).
//   2. A HITL APPROVAL GATE. The only side-effecting action ("send_outreach") cannot fire on the
//      agent's say-so; it parks in `awaiting_approval` until a human approves.
// Every decision is logged with its reason.

import { MockProvider, type CompletionRequest, type CompletionResponse } from "../../../../tools/mock-llm/index.ts";
import { Enrichment, Score } from "./schema.ts";
import { Tracer } from "./harness.ts";
import { COST_CAP_USD, STEP_CEILING_USD, costOfUsage, roundUsd } from "./cost.ts";

export interface Lead {
  id: string;
  blurb: string;
}

// The terminal disposition of a lead after its inner loop runs.
export type Decision =
  | "awaiting_approval" // recommended send_outreach + human approved -> queued to send
  | "rejected" // recommended send_outreach + human rejected -> not sent
  | "auto_nurture" // recommended nurture -> auto, no human needed
  | "auto_disqualify" // recommended disqualify -> auto, no human needed
  | "budget_exhausted"; // a step was refused pre-execution because it would breach the cap

export interface LeadResult {
  id: string;
  company: string | null;
  fit: number | null;
  recommendedAction: string | null;
  decision: Decision;
  reason: string;
  costUsd: number; // actual spend on THIS lead — guaranteed <= COST_CAP_USD
  approved: boolean | null; // HITL outcome, or null if no gate was reached
  steps: string[]; // ordered step log for this lead
}

// HITL approval is injected so the run is deterministic (no prompt) and tests can drive it directly.
export type ApprovalFn = (lead: Lead, fit: number) => boolean;

// --- prompt builders (single source of truth: the record step and the agent MUST agree, or the
// request hash won't match the recorded fixture) ---

export const ENRICH_SYSTEM =
  "You are an outbound SDR enrichment assistant. Given a raw lead blurb, reply with ONLY a JSON object " +
  '{"company": string, "segment": one of ["smb","mid-market","enterprise"], "persona": string}.';

export const SCORE_SYSTEM =
  "You are an outbound SDR scoring assistant. Given the enriched lead, reply with ONLY a JSON object " +
  '{"fit": integer 0-100, "recommended_action": one of ["send_outreach","nurture","disqualify"]}.';

export function enrichRequest(lead: Lead): CompletionRequest {
  return { system: ENRICH_SYSTEM, messages: [{ role: "user", content: lead.blurb }], tools: [] };
}

export function scoreRequest(lead: Lead, enrichment: Enrichment): CompletionRequest {
  return {
    system: SCORE_SYSTEM,
    messages: [{ role: "user", content: `${lead.blurb}\n\nEnriched: ${JSON.stringify(enrichment)}` }],
    tools: [],
  };
}

// Map a (parsed) score to a terminal decision. The only path that needs a human is send_outreach.
export function decideAction(action: Score["recommended_action"], approved: boolean): Decision {
  if (action === "nurture") return "auto_nurture";
  if (action === "disqualify") return "auto_disqualify";
  // send_outreach is side-effecting -> gated.
  return approved ? "awaiting_approval" : "rejected";
}

// The INNER agent loop for one lead, with the pre-execution budget cap wrapped around every step.
export function processLead(
  lead: Lead,
  provider: MockProvider,
  tracer: Tracer,
  approve: ApprovalFn,
): LeadResult {
  let spent = 0;
  const steps: string[] = [];

  // Returns true if the next step fits under the cap; otherwise logs budget_exhausted and returns false.
  // It RESERVES the per-step ceiling (the step's max possible cost) and refuses if that reservation
  // would breach the cap — BEFORE the provider call. This is the pre-execution guarantee.
  const canAfford = (step: string): boolean => {
    const projected = roundUsd(spent + STEP_CEILING_USD);
    if (projected > COST_CAP_USD) {
      tracer.emit("decision", "rejected", {
        lead_id: lead.id,
        step,
        reason: "budget_exhausted",
        spent_usd: spent,
        cap_usd: COST_CAP_USD,
        projected_usd: projected,
      });
      steps.push(`${step}:budget_exhausted`);
      return false;
    }
    return true;
  };

  const charge = (resp: CompletionResponse): void => {
    const c = costOfUsage(resp.usage);
    // Enforce the max_tokens bound: a step's actual cost can never exceed the reserved ceiling. If it
    // did, the pre-execution reservation would be a lie and a single step could breach the cap.
    if (c > STEP_CEILING_USD) {
      throw new Error(
        `step cost $${c} exceeds the per-step ceiling $${STEP_CEILING_USD} (max_tokens bound violated)`,
      );
    }
    spent = roundUsd(spent + c);
  };

  // --- step 1: enrich ---
  if (!canAfford("enrich")) {
    return budgetStopped(lead, null, null, null, spent, steps);
  }
  const enrichResp = provider.complete(enrichRequest(lead));
  charge(enrichResp);
  const enrichment = Enrichment.parse(JSON.parse(String(enrichResp.content)));
  steps.push("enrich");
  tracer.emit("llm_call", "ok", {
    lead_id: lead.id,
    step: "enrich",
    company: enrichment.company,
    cost_usd: spent,
  });

  // --- step 2: score (cap re-checked first — a fat enrich response can exhaust the budget here) ---
  if (!canAfford("score")) {
    return budgetStopped(lead, enrichment.company, null, null, spent, steps);
  }
  const scoreResp = provider.complete(scoreRequest(lead, enrichment));
  charge(scoreResp);
  const score = Score.parse(JSON.parse(String(scoreResp.content)));
  steps.push("score");
  tracer.emit("llm_call", "ok", {
    lead_id: lead.id,
    step: "score",
    fit: score.fit,
    recommended_action: score.recommended_action,
    cost_usd: spent,
  });

  // --- step 3: decide next action, with the HITL gate for the side-effecting path ---
  let approved: boolean | null = null;
  if (score.recommended_action === "send_outreach") {
    approved = approve(lead, score.fit);
    tracer.emit("approval", approved ? "ok" : "rejected", {
      lead_id: lead.id,
      action: "send_outreach",
      fit: score.fit,
      approved,
    });
  }
  const decision = decideAction(score.recommended_action, approved ?? false);
  const reason = reasonFor(decision, score.fit);
  steps.push(`decide:${decision}`);
  tracer.emit("decision", decision === "rejected" ? "rejected" : "ok", {
    lead_id: lead.id,
    recommended_action: score.recommended_action,
    decision,
    reason,
    fit: score.fit,
    cost_usd: spent,
  });

  return {
    id: lead.id,
    company: enrichment.company,
    fit: score.fit,
    recommendedAction: score.recommended_action,
    decision,
    reason,
    costUsd: spent,
    approved,
    steps,
  };
}

function budgetStopped(
  lead: Lead,
  company: string | null,
  fit: number | null,
  recommendedAction: string | null,
  spent: number,
  steps: string[],
): LeadResult {
  return {
    id: lead.id,
    company,
    fit,
    recommendedAction,
    decision: "budget_exhausted",
    reason: `pre-execution cap of $${COST_CAP_USD} would be breached; remaining steps not executed`,
    costUsd: spent,
    approved: null,
    steps,
  };
}

function reasonFor(decision: Decision, fit: number): string {
  switch (decision) {
    case "awaiting_approval":
      return `fit ${fit} >= outreach bar; human approved, queued to send`;
    case "rejected":
      return `fit ${fit} flagged for outreach but human rejected; not sent`;
    case "auto_nurture":
      return `fit ${fit} below outreach bar; auto-nurtured (no side effect, no human)`;
    case "auto_disqualify":
      return `fit ${fit} too low; auto-disqualified (no side effect, no human)`;
    case "budget_exhausted":
      return `pre-execution cap of $${COST_CAP_USD} would be breached`;
  }
}
