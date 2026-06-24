import { z } from "zod";

// Structured-output contracts for the two inner LLM steps (the **G**oals surface in practice).

// enrich: the model returns firmographic context inferred from the raw lead blurb.
export const Enrichment = z.object({
  company: z.string(),
  segment: z.enum(["smb", "mid-market", "enterprise"]),
  persona: z.string(),
});
export type Enrichment = z.infer<typeof Enrichment>;

// score: the model rates fit 0-100 and recommends an action. "send_outreach" is side-effecting and
// therefore gated behind HITL approval; "nurture"/"disqualify" are non-side-effecting auto-actions.
export const Score = z.object({
  fit: z.number().int().min(0).max(100),
  recommended_action: z.enum(["send_outreach", "nurture", "disqualify"]),
});
export type Score = z.infer<typeof Score>;
