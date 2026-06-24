import { describe, it, expect } from "vitest";
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { MockProvider } from "../../../../tools/mock-llm/index.ts";
import { optimize, type Task } from "../src/agent.ts";
import { Tracer } from "../src/harness.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const provider = new MockProvider(path.join(here, "..", "fixtures"));

interface TaskFile extends Task {
  gate: number;
  maxIterations: number;
}
const taskFile: TaskFile = JSON.parse(
  readFileSync(path.join(here, "..", "eval", "task.json"), "utf-8"),
);
const task: Task = { id: taskFile.id, brief: taskFile.brief, rubric: taskFile.rubric };

function tracer() {
  return new Tracer("test", { name: "evaluator-optimizer", capability_tier: "L1" });
}

function run() {
  return optimize(task, provider, tracer(), taskFile.gate, taskFile.maxIterations);
}

describe("evaluator-optimizer loop", () => {
  it("crosses the rubric gate — final score >= gate", () => {
    const outcome = run();
    expect(outcome.gatePassed).toBe(true);
    expect(outcome.finalScore).toBeGreaterThanOrEqual(taskFile.gate);
  });

  it("climbs the score monotonically (non-decreasing) across iterations", () => {
    const scores = run().ledger.map((r) => r.score);
    expect(scores.length).toBeGreaterThan(1);
    for (let i = 1; i < scores.length; i++) {
      expect(scores[i]).toBeGreaterThanOrEqual(scores[i - 1]);
    }
  });

  it("stops as soon as the gate is met (does not burn the whole iteration budget)", () => {
    const outcome = run();
    // Only the last iteration passes; every earlier one is below the gate (it kept revising).
    expect(outcome.iterations).toBeLessThanOrEqual(taskFile.maxIterations);
    expect(outcome.ledger[outcome.ledger.length - 1].passed).toBe(true);
    for (const r of outcome.ledger.slice(0, -1)) {
      expect(r.passed).toBe(false);
      expect(r.score).toBeLessThan(taskFile.gate);
    }
  });

  it("records the score-climb ledger with one row per iteration", () => {
    const outcome = run();
    outcome.ledger.forEach((r, idx) => expect(r.iteration).toBe(idx + 1));
    expect(outcome.finalScore).toBe(outcome.ledger[outcome.ledger.length - 1].score);
  });

  it("throws MissingFixtureError on an unrecorded task (a drifted prompt fails loudly)", () => {
    const drifted: Task = { id: "x", brief: "never recorded", rubric: "never recorded" };
    expect(() => optimize(drifted, provider, tracer(), taskFile.gate, taskFile.maxIterations)).toThrow();
  });
});
