import { z } from "zod";

// Structured output contract for the evaluator (the **E**valuation surface in practice): a numeric
// score in [0, 1] against the rubric plus a short critique the reviser can act on.
export const Evaluation = z.object({
  score: z.number().min(0).max(1),
  critique: z.string(),
});
export type Evaluation = z.infer<typeof Evaluation>;
