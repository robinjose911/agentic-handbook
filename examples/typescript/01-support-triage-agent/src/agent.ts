// The support-triage agent: classify a ticket (one LLM call, structured output) then route it. Low
// confidence / unparseable output escalates to human-review (basic HITL). The simplest viable agent.

import { MockProvider, type CompletionRequest } from "../../../../tools/mock-llm/index.ts";
import { Classification } from "./schema.ts";
import { Tracer } from "./harness.ts";

export interface Ticket {
  id: string;
  text: string;
}
export type Route = "billing" | "technical" | "account" | "human-review";

// Single source of the classifier prompt — the record step and the agent MUST agree, or the request
// hash won't match the recorded fixture.
export const SYSTEM =
  "You are a support triage classifier. Read the customer ticket and reply with ONLY a JSON object " +
  '{"intent": one of ["billing","technical","account","other"], "urgency": one of ["low","medium","high"]}.';

export function classifyRequest(ticket: Ticket): CompletionRequest {
  return { system: SYSTEM, messages: [{ role: "user", content: ticket.text }], tools: [] };
}

export function decideRoute(c: Classification): Route {
  // High-urgency account/billing issues and any "other" intent go to a human; the rest auto-route.
  if (c.intent === "other") return "human-review";
  return c.intent;
}

export function classifyAndRoute(
  ticket: Ticket,
  provider: MockProvider,
  tracer: Tracer,
): { classification: Classification; route: Route } {
  const resp = provider.complete(classifyRequest(ticket));
  let parsed: ReturnType<typeof Classification.safeParse>;
  try {
    parsed = Classification.safeParse(JSON.parse(String(resp.content)));
  } catch {
    parsed = { success: false } as ReturnType<typeof Classification.safeParse>;
  }
  if (!parsed.success) {
    tracer.emit("escalation", "escalated", { ticket_id: ticket.id, reason: "unparseable_classification" });
    return { classification: { intent: "other", urgency: "low" }, route: "human-review" };
  }
  tracer.emit("llm_call", "ok", { ticket_id: ticket.id, intent: parsed.data.intent });
  const route = decideRoute(parsed.data);
  tracer.emit("decision", "ok", {
    ticket_id: ticket.id,
    intent: parsed.data.intent,
    urgency: parsed.data.urgency,
    route,
  });
  return { classification: parsed.data, route };
}
