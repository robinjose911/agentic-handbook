// Entrypoint: run the evaluator-optimizer loop on one task against the mock provider, then write the
// receipts: trace.jsonl, eval-report.json, receipt.json. Deterministic — re-running is a no-op diff.
//
//   node --experimental-strip-types run.ts

import { readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { MockProvider } from "../../../tools/mock-llm/index.ts";
import { optimize, type Task } from "./src/agent.ts";
import { Tracer, stableStringify } from "./src/harness.ts";

const here = path.dirname(fileURLToPath(import.meta.url));

interface TaskFile extends Task {
  gate: number;
  maxIterations: number;
}

const taskFile: TaskFile = JSON.parse(readFileSync(path.join(here, "eval", "task.json"), "utf-8"));
const task: Task = { id: taskFile.id, brief: taskFile.brief, rubric: taskFile.rubric };
const GATE = taskFile.gate;

const provider = new MockProvider(path.join(here, "fixtures"));
const tracer = new Tracer("trace-evaluator-optimizer", {
  name: "evaluator-optimizer",
  capability_tier: "L1",
});

const outcome = optimize(task, provider, tracer, GATE, taskFile.maxIterations);

// Format a fixed-2dp score string used in every artifact + headline so the prose-vs-receipt gate holds.
const fmt = (n: number): string => n.toFixed(2);

const ledger = outcome.ledger.map((r) => ({
  iteration: r.iteration,
  score: r.score,
  passed: r.passed,
}));
const scoreClimb = outcome.ledger.map((r) => fmt(r.score)).join(" -> ");

const evalReport = {
  suite: "headline-evaluator-optimizer",
  gate: GATE,
  iterations: outcome.iterations,
  finalScore: outcome.finalScore,
  gatePassed: outcome.gatePassed,
  scoreClimb,
  ledger,
};

const receipt = {
  example: "03-evaluator-optimizer-self-improving",
  task: task.id,
  gate: GATE,
  finalScore: outcome.finalScore,
  gatePassed: outcome.gatePassed,
  iterations: outcome.iterations,
  finalDraft: outcome.finalDraft,
  traceEvents: tracer.events.length,
  // headline: every value here MUST appear verbatim in README.md (the prose-vs-receipt gate).
  headline: {
    iterations: outcome.iterations,
    finalScore: fmt(outcome.finalScore),
    gate: fmt(GATE),
    gatePassed: outcome.gatePassed,
    scoreClimb,
    traceEvents: tracer.events.length,
  },
};

writeFileSync(path.join(here, "trace.jsonl"), tracer.toJsonl());
writeFileSync(path.join(here, "eval-report.json"), stableStringify(evalReport));
writeFileSync(path.join(here, "receipt.json"), stableStringify(receipt));

console.log(
  `evaluator-optimizer: ${outcome.iterations} iterations, ` +
    `score ${scoreClimb}, final ${fmt(outcome.finalScore)} (gate ${fmt(GATE)}, passed ${outcome.gatePassed})`,
);
if (!outcome.gatePassed) process.exit(1);
