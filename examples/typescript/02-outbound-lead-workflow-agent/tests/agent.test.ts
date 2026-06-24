import { describe, it, expect } from "vitest";
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { MockProvider } from "../../../../tools/mock-llm/index.ts";
import { processLead, decideAction, type Lead } from "../src/agent.ts";
import { Tracer } from "../src/harness.ts";
import { COST_CAP_USD } from "../src/cost.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const fixtures = path.join(here, "..", "fixtures");
const provider = new MockProvider(fixtures);

interface LeadCase extends Lead {
  expectedDecision: string;
  approve: boolean;
}
const leads: LeadCase[] = JSON.parse(readFileSync(path.join(here, "..", "eval", "leads.json"), "utf-8"));

function tracer() {
  return new Tracer("test", { name: "outbound-lead-workflow", capability_tier: "L2" });
}
function run(c: LeadCase) {
  return processLead({ id: c.id, blurb: c.blurb }, provider, tracer(), () => c.approve);
}
function byId(id: string) {
  const c = leads.find((l) => l.id === id);
  if (!c) throw new Error(`no lead ${id}`);
  return c;
}

describe("decideAction", () => {
  it("auto-routes nurture / disqualify without a human", () => {
    expect(decideAction("nurture", false)).toBe("auto_nurture");
    expect(decideAction("disqualify", false)).toBe("auto_disqualify");
  });
  it("gates send_outreach behind HITL approval", () => {
    expect(decideAction("send_outreach", true)).toBe("awaiting_approval");
    expect(decideAction("send_outreach", false)).toBe("rejected");
  });
});

describe("HITL approval gate", () => {
  it("approved outreach parks in awaiting_approval", () => {
    const r = run(byId("l1"));
    expect(r.recommendedAction).toBe("send_outreach");
    expect(r.decision).toBe("awaiting_approval");
    expect(r.approved).toBe(true);
  });
  it("rejected outreach is not sent", () => {
    const r = run(byId("l2"));
    expect(r.recommendedAction).toBe("send_outreach");
    expect(r.decision).toBe("rejected");
    expect(r.approved).toBe(false);
  });
});

describe("pre-execution budget cap", () => {
  it("stops the fat lead at the score step with budget_exhausted (score never executed)", () => {
    const t = tracer();
    const r = processLead({ id: "l3", blurb: byId("l3").blurb }, provider, t, () => false);
    expect(r.decision).toBe("budget_exhausted");
    // enrich ran, score did NOT.
    expect(r.steps).toContain("enrich");
    expect(r.steps).toContain("score:budget_exhausted");
    expect(r.steps).not.toContain("score");
    // it logged the refusal as a rejected decision event.
    expect(t.events.some((e) => e.status === "rejected")).toBe(true);
  });

  it("EVERY lead's actual cost stays at or under the cap (maxLeadCostUsd <= costCapUsd)", () => {
    const maxLeadCostUsd = leads.reduce((m, c) => Math.max(m, run(c).costUsd), 0);
    expect(maxLeadCostUsd).toBeLessThanOrEqual(COST_CAP_USD);
  });
});

describe("loud failure on drift", () => {
  it("throws MissingFixtureError on an unrecorded lead", () => {
    expect(() =>
      processLead({ id: "x", blurb: "a lead never recorded as a fixture" }, provider, tracer(), () => false),
    ).toThrow();
  });
});

describe("receipt invariants", () => {
  it("the committed receipt honors the cap (budgetHonored true, maxLeadCostUsd <= costCapUsd)", () => {
    const receipt = JSON.parse(readFileSync(path.join(here, "..", "receipt.json"), "utf-8"));
    expect(receipt.budgetHonored).toBe(true);
    expect(receipt.maxLeadCostUsd).toBeLessThanOrEqual(receipt.costCapUsd);
    expect(receipt.headline.budgetHonored).toBe(true);
    expect(receipt.headline.maxLeadCostUsd).toBeLessThanOrEqual(receipt.headline.costCapUsd);
  });
});
