// Record step (OFF in CI). Authors the canned mock-provider fixtures from the leads set so the example
// runs offline. Re-run only when a prompt or a lead input changes:
//
//   node --experimental-strip-types record-fixtures.ts
//
// There is no real-provider call here — the canned enrichments/scores ARE the leads-set labels, which
// is what makes the run deterministic and the eval a test of the workflow/budget/HITL logic, not the
// model. Note the recorded `usage` token counts: they are the input to the cost model, so lead l3's
// deliberately fat enrich response is what drives it over the per-lead budget cap at the score step.

import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { record } from "../../../tools/mock-llm/index.ts";
import { enrichRequest, scoreRequest, type Lead } from "./src/agent.ts";
import type { Enrichment } from "./src/schema.ts";

interface LeadFixture extends Lead {
  enrich: Enrichment;
  enrichUsage: { input_tokens: number; output_tokens: number };
  score: { fit: number; recommended_action: string };
  scoreUsage: { input_tokens: number; output_tokens: number };
}

const here = path.dirname(fileURLToPath(import.meta.url));
const leads: LeadFixture[] = JSON.parse(readFileSync(path.join(here, "eval", "leads.json"), "utf-8"));
const fixturesDir = path.join(here, "fixtures");

let n = 0;
for (const lead of leads) {
  // enrich fixture
  record(
    enrichRequest(lead),
    { content: JSON.stringify(lead.enrich), stop_reason: "end_turn", usage: lead.enrichUsage },
    fixturesDir,
  );
  n++;
  // score fixture (request includes the enriched object, so it must be recorded with the SAME shape)
  record(
    scoreRequest(lead, lead.enrich),
    { content: JSON.stringify(lead.score), stop_reason: "end_turn", usage: lead.scoreUsage },
    fixturesDir,
  );
  n++;
}
console.log(`recorded ${n} fixtures into ${path.relative(here, fixturesDir)}/`);
