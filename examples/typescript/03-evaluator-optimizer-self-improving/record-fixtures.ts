// Record step (OFF in CI). Authors the canned mock-provider fixtures for the evaluator-optimizer loop
// from the task script (eval/task.json) so the example runs offline. Re-run only when a prompt or the
// task script changes:
//
//   node --experimental-strip-types record-fixtures.ts
//
// There is no real-provider call here — the canned drafts/scores ARE the score-climb ledger, which is
// what makes the run deterministic and the eval a test of the loop logic (does the gate stop the loop?),
// not of the model. The recorded scores climb 0.55 -> 0.72 -> 0.88 and cross the gate of 0.85 at
// iteration 3, so the agent makes exactly: 1 generate + 3 evaluates + 2 revises.

import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { record } from "../../../tools/mock-llm/index.ts";
import { generateRequest, evaluateRequest, reviseRequest, type Task } from "./src/agent.ts";

interface ScriptStep {
  iteration: number;
  draft: string;
  score: number;
  critique: string;
}
interface TaskFile extends Task {
  gate: number;
  maxIterations: number;
  script: ScriptStep[];
}

const here = path.dirname(fileURLToPath(import.meta.url));
const taskFile: TaskFile = JSON.parse(readFileSync(path.join(here, "eval", "task.json"), "utf-8"));
const fixturesDir = path.join(here, "fixtures");
const task: Task = { id: taskFile.id, brief: taskFile.brief, rubric: taskFile.rubric };
const { script, gate, maxIterations } = taskFile;

let n = 0;
function rec(req: ReturnType<typeof generateRequest>, content: string): void {
  record(req, { content, stop_reason: "end_turn", usage: { input_tokens: 48, output_tokens: 16 } }, fixturesDir);
  n++;
}

// Replay the exact call sequence the agent will make so every fixture is hit (and none are orphaned).
// 1) generate the first draft from the brief.
rec(generateRequest(task), script[0].draft);

for (let i = 1; i <= maxIterations; i++) {
  const step = script[i - 1];
  // 2) evaluate the current draft -> {score, critique}.
  rec(
    evaluateRequest(task, step.draft),
    JSON.stringify({ score: step.score, critique: step.critique }),
  );
  const passed = step.score >= gate;
  if (passed || i === maxIterations) break;
  // 3) revise the current draft with its critique -> the next draft.
  rec(reviseRequest(task, step.draft, step.critique), script[i].draft);
}

console.log(`recorded ${n} fixtures into ${path.relative(here, fixturesDir)}/`);
