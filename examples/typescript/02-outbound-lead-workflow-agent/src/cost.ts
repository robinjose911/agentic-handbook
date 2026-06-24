// The pre-execution budget cap is the whole point of this example, so the cost model lives in one
// place and is shared by the agent (which enforces the cap) and the tests (which assert it holds).
//
// Illustrative pricing only (a Haiku-class tariff) — labelled, not load-bearing on any real vendor.

import type { CompletionResponse } from "../../../../tools/mock-llm/index.ts";

// USD per 1,000 tokens. Self-reported / illustrative — verify before relying.
export const PRICE_PER_1K_INPUT_USD = 0.003;
export const PRICE_PER_1K_OUTPUT_USD = 0.015;

// Hard pre-execution cap, per lead.
export const COST_CAP_USD = 0.015;

// Each step is sent with a bounded max_tokens, so its cost can never exceed STEP_CEILING_USD (a
// generous input allowance + the output bound). Before a step runs we RESERVE this ceiling against the
// cap; if (already-spent + ceiling) would exceed the cap, the step is refused BEFORE the provider call
// — the cap is pre-execution, and `chargeStep` asserts the actual cost never exceeds the ceiling, so a
// single over-ceiling step can never slip through and breach the cap.
export const MAX_OUTPUT_TOKENS = 512;
export const STEP_CEILING_USD = 0.01;

// Round to whole micro-dollars so the artifacts are byte-stable (no float-formatting drift).
export function roundUsd(usd: number): number {
  return Math.round(usd * 1e6) / 1e6;
}

export function costOfUsage(usage: CompletionResponse["usage"]): number {
  const input = usage?.input_tokens ?? 0;
  const output = usage?.output_tokens ?? 0;
  const usd = (input / 1000) * PRICE_PER_1K_INPUT_USD + (output / 1000) * PRICE_PER_1K_OUTPUT_USD;
  return roundUsd(usd);
}
