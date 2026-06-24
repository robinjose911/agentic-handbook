// The evaluator-optimizer (self-improving) agent: generate a draft, score it against a rubric, and if
// the score is below the gate, feed the critique back into a reviser and try again — looping until the
// rubric gate is met or an iteration cap is hit. The output is a "score-climb ledger": the score must
// climb across iterations and cross the gate. This owns the **evaluator-optimizer** pattern from the
// pattern catalog (generate -> critique-against-a-rubric -> revise).

import { MockProvider, type CompletionRequest } from "../../../../tools/mock-llm/index.ts";
import { Evaluation } from "./schema.ts";
import { Tracer } from "./harness.ts";

export interface Task {
  id: string;
  // The thing we are iteratively improving — here, the brief for a product-page headline.
  brief: string;
  rubric: string;
}

// Single source of every prompt — the record step and the agent MUST agree, or the request hash won't
// match the recorded fixture. Each builder is a pure function of its inputs (no clock, no RNG).

export const GENERATOR_SYSTEM =
  "You are a senior copywriter. Read the brief and write ONE product-page headline. " +
  "Reply with ONLY the headline text — no quotes, no preamble.";

export const EVALUATOR_SYSTEM =
  "You are a strict copy editor scoring a headline against a rubric. Reply with ONLY a JSON object " +
  '{"score": a number in [0,1], "critique": a one-sentence note on the single biggest improvement}.';

export const REVISER_SYSTEM =
  "You are a senior copywriter revising a headline. Apply the editor's critique to the current " +
  "headline and reply with ONLY the improved headline text — no quotes, no preamble.";

export function generateRequest(task: Task): CompletionRequest {
  return {
    system: GENERATOR_SYSTEM,
    messages: [{ role: "user", content: `Brief: ${task.brief}` }],
    tools: [],
  };
}

export function evaluateRequest(task: Task, draft: string): CompletionRequest {
  return {
    system: EVALUATOR_SYSTEM,
    messages: [{ role: "user", content: `Rubric: ${task.rubric}\nHeadline: ${draft}` }],
    tools: [],
  };
}

export function reviseRequest(task: Task, draft: string, critique: string): CompletionRequest {
  return {
    system: REVISER_SYSTEM,
    messages: [
      { role: "user", content: `Brief: ${task.brief}\nCurrent headline: ${draft}\nCritique: ${critique}` },
    ],
    tools: [],
  };
}

export interface IterationResult {
  iteration: number;
  draft: string;
  score: number;
  critique: string;
  passed: boolean;
}

export interface OptimizeOutcome {
  ledger: IterationResult[];
  finalDraft: string;
  finalScore: number;
  iterations: number;
  gatePassed: boolean;
}

function evaluate(task: Task, draft: string, provider: MockProvider): Evaluation {
  const resp = provider.complete(evaluateRequest(task, draft));
  // The evaluator is a structured-output contract; an unparseable score is a hard failure, not a guess.
  return Evaluation.parse(JSON.parse(String(resp.content)));
}

// Run the generate -> evaluate -> revise loop until the rubric gate is met or `maxIterations` is hit.
export function optimize(
  task: Task,
  provider: MockProvider,
  tracer: Tracer,
  gate: number,
  maxIterations: number,
): OptimizeOutcome {
  const ledger: IterationResult[] = [];

  // Iteration 1: the generator produces the first draft from the brief alone.
  let draft = String(provider.complete(generateRequest(task)).content).trim();
  tracer.emit("llm_call", "ok", { task_id: task.id, phase: "generate", iteration: 1 });

  for (let i = 1; i <= maxIterations; i++) {
    const evaluation = evaluate(task, draft, provider);
    const score = evaluation.score;
    const passed = score >= gate;
    tracer.emit("llm_call", "ok", {
      task_id: task.id,
      phase: "evaluate",
      iteration: i,
      score,
    });
    tracer.emit("decision", passed ? "ok" : "escalated", {
      task_id: task.id,
      iteration: i,
      score,
      gate,
      passed,
      action: passed ? "accept" : "revise",
    });
    ledger.push({ iteration: i, draft, score, critique: evaluation.critique, passed });

    if (passed || i === maxIterations) break;

    // Below the gate and budget remains: revise the draft with the critique and loop.
    draft = String(provider.complete(reviseRequest(task, draft, evaluation.critique)).content).trim();
    tracer.emit("llm_call", "ok", { task_id: task.id, phase: "revise", iteration: i + 1 });
  }

  const last = ledger[ledger.length - 1];
  return {
    ledger,
    finalDraft: last.draft,
    finalScore: last.score,
    iterations: ledger.length,
    gatePassed: last.passed,
  };
}
