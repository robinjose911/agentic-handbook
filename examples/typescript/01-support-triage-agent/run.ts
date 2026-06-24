// Entrypoint: run the agent over the golden set against the mock provider, then write the receipts:
// trace.jsonl, eval-report.json, receipt.json. Deterministic — re-running is a no-op diff.
//
//   node --experimental-strip-types run.ts

import { readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { MockProvider } from "../../../tools/mock-llm/index.ts";
import { classifyAndRoute, type Ticket } from "./src/agent.ts";
import { Tracer, stableStringify } from "./src/harness.ts";

const here = path.dirname(fileURLToPath(import.meta.url));

interface GoldenCase extends Ticket {
  urgency: string;
  expectedIntent: string;
  expectedRoute: string;
}

const golden: GoldenCase[] = JSON.parse(readFileSync(path.join(here, "eval", "golden.json"), "utf-8"));
const provider = new MockProvider(path.join(here, "fixtures"));
const tracer = new Tracer("trace-support-triage", { name: "support-triage", capability_tier: "L1" });

const GATE = 0.8;
const cases = golden.map((g) => {
  const { classification, route } = classifyAndRoute({ id: g.id, text: g.text }, provider, tracer);
  return {
    id: g.id,
    expectedIntent: g.expectedIntent,
    gotIntent: classification.intent,
    expectedRoute: g.expectedRoute,
    gotRoute: route,
    pass: classification.intent === g.expectedIntent && route === g.expectedRoute,
  };
});

const passed = cases.filter((c) => c.pass).length;
const total = cases.length;
const passRate = Number((passed / total).toFixed(4));

const evalReport = { suite: "support-triage-classification", gate: GATE, passRate, passed, total, cases };
const receipt = {
  example: "01-support-triage-agent",
  classificationPassRate: passRate,
  passed,
  total,
  gate: GATE,
  gatePassed: passRate >= GATE,
  routes: cases.map((c) => ({ id: c.id, route: c.gotRoute })),
  traceEvents: tracer.events.length,
  // headline: every value here MUST appear verbatim in README.md (the prose-vs-receipt gate).
  headline: {
    classificationPassRate: `${Math.round(passRate * 100)}%`,
    casesPassed: `${passed}/${total}`,
    traceEvents: tracer.events.length,
  },
};

writeFileSync(path.join(here, "trace.jsonl"), tracer.toJsonl());
writeFileSync(path.join(here, "eval-report.json"), stableStringify(evalReport));
writeFileSync(path.join(here, "receipt.json"), stableStringify(receipt));

console.log(`support-triage: ${passed}/${total} pass (rate ${passRate}, gate ${GATE})`);
if (!receipt.gatePassed) process.exit(1);
