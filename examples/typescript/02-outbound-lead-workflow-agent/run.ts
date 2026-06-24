// Entrypoint: the OUTER outbound-lead workflow. It iterates the leads set, runs each lead's inner agent
// loop (enrich -> score -> decide, under a per-lead budget cap with a HITL gate), then writes the
// receipts: trace.jsonl, eval-report.json, receipt.json. Deterministic — re-running is a no-op diff.
//
//   node --experimental-strip-types run.ts

import { readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { MockProvider } from "../../../tools/mock-llm/index.ts";
import { processLead, type Lead, type LeadResult } from "./src/agent.ts";
import { Tracer, stableStringify } from "./src/harness.ts";
import { COST_CAP_USD } from "./src/cost.ts";

const here = path.dirname(fileURLToPath(import.meta.url));

interface LeadCase extends Lead {
  expectedAction: string;
  expectedDecision: string;
  approve: boolean; // canned HITL outcome for this lead (deterministic stand-in for a human)
}

const leads: LeadCase[] = JSON.parse(readFileSync(path.join(here, "eval", "leads.json"), "utf-8"));
const provider = new MockProvider(path.join(here, "fixtures"));
const tracer = new Tracer("trace-outbound-lead-workflow", {
  name: "outbound-lead-workflow",
  capability_tier: "L2",
});

// The OUTER durable-style workflow: process each lead in order, collecting its result.
const results: LeadResult[] = leads.map((lead) =>
  processLead({ id: lead.id, blurb: lead.blurb }, provider, tracer, () => lead.approve),
);

// Per-lead eval: did the decision land where the leads set says it should?
const cases = results.map((r, i) => {
  const want = leads[i];
  return {
    id: r.id,
    expectedDecision: want.expectedDecision,
    gotDecision: r.decision,
    company: r.company,
    fit: r.fit,
    recommendedAction: r.recommendedAction,
    costUsd: r.costUsd,
    underCap: r.costUsd <= COST_CAP_USD,
    pass: r.decision === want.expectedDecision && r.costUsd <= COST_CAP_USD,
  };
});

const passed = cases.filter((c) => c.pass).length;
const total = cases.length;

// Cross-lead aggregate.
const approved = results.filter((r) => r.decision === "awaiting_approval").length;
const rejected = results.filter((r) => r.decision === "rejected").length;
const autoNurtured = results.filter((r) => r.decision === "auto_nurture").length;
const autoDisqualified = results.filter((r) => r.decision === "auto_disqualify").length;
const budgetStopped = results.filter((r) => r.decision === "budget_exhausted").length;
const maxLeadCostUsd = results.reduce((m, r) => Math.max(m, r.costUsd), 0);
const budgetHonored = results.every((r) => r.costUsd <= COST_CAP_USD);

const evalReport = {
  suite: "outbound-lead-workflow",
  costCapUsd: COST_CAP_USD,
  maxLeadCostUsd,
  budgetHonored,
  aggregate: {
    leadsProcessed: total,
    approved,
    rejected,
    autoNurtured,
    autoDisqualified,
    budgetStopped,
  },
  passed,
  total,
  cases,
};

const receipt = {
  example: "02-outbound-lead-workflow-agent",
  costCapUsd: COST_CAP_USD,
  maxLeadCostUsd,
  budgetHonored,
  leadsProcessed: total,
  approved,
  rejected,
  autoNurtured,
  autoDisqualified,
  budgetStopped,
  passed,
  total,
  traceEvents: tracer.events.length,
  // headline: every value here MUST appear verbatim in README.md (the prose-vs-receipt gate).
  headline: {
    costCapUsd: COST_CAP_USD,
    maxLeadCostUsd,
    budgetHonored: true,
    leadsProcessed: total,
    traceEvents: tracer.events.length,
  },
};

writeFileSync(path.join(here, "trace.jsonl"), tracer.toJsonl());
writeFileSync(path.join(here, "eval-report.json"), stableStringify(evalReport));
writeFileSync(path.join(here, "receipt.json"), stableStringify(receipt));

console.log(
  `outbound-lead-workflow: ${total} leads | approved ${approved}, rejected ${rejected}, ` +
    `nurture ${autoNurtured}, disqualify ${autoDisqualified}, budget-stopped ${budgetStopped} | ` +
    `maxLeadCost $${maxLeadCostUsd} (cap $${COST_CAP_USD}) | eval ${passed}/${total}`,
);
// Fail loudly if the cap was ever breached — the whole point of the example.
if (!budgetHonored) process.exit(1);
if (passed !== total) process.exit(1);
