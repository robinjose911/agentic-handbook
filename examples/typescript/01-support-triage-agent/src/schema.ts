import { z } from "zod";

// Structured output contract for the classifier (the **G**oals surface in practice).
export const Classification = z.object({
  intent: z.enum(["billing", "technical", "account", "other"]),
  urgency: z.enum(["low", "medium", "high"]),
});
export type Classification = z.infer<typeof Classification>;
