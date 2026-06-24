import { describe, it, expect } from "vitest";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { MockProvider } from "../../../../tools/mock-llm/index.ts";
import { classifyAndRoute, decideRoute } from "../src/agent.ts";
import { Tracer } from "../src/harness.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const provider = new MockProvider(path.join(here, "..", "fixtures"));

function tracer() {
  return new Tracer("test", { name: "support-triage", capability_tier: "L1" });
}

describe("decideRoute", () => {
  it("auto-routes known intents", () => {
    expect(decideRoute({ intent: "billing", urgency: "high" })).toBe("billing");
    expect(decideRoute({ intent: "technical", urgency: "low" })).toBe("technical");
    expect(decideRoute({ intent: "account", urgency: "medium" })).toBe("account");
  });
  it("escalates an 'other' intent to a human", () => {
    expect(decideRoute({ intent: "other", urgency: "low" })).toBe("human-review");
  });
});

describe("classifyAndRoute", () => {
  it("classifies and routes a billing ticket from its recorded fixture", () => {
    const t = tracer();
    const { classification, route } = classifyAndRoute(
      { id: "t1", text: "My card was declined when I tried to pay the invoice." },
      provider,
      t,
    );
    expect(classification.intent).toBe("billing");
    expect(route).toBe("billing");
    expect(t.events.length).toBeGreaterThan(0);
  });

  it("escalates a chit-chat ticket to human-review", () => {
    const t = tracer();
    const { route } = classifyAndRoute(
      { id: "t5", text: "Can you tell me a joke about kubernetes?" },
      provider,
      t,
    );
    expect(route).toBe("human-review");
  });

  it("throws MissingFixtureError on an unrecorded ticket (a drifted prompt fails loudly)", () => {
    const t = tracer();
    expect(() =>
      classifyAndRoute({ id: "x", text: "a ticket never recorded as a fixture" }, provider, t),
    ).toThrow();
  });
});
