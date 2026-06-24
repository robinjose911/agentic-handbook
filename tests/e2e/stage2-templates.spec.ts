// Stage 2 integration test: the templates index lists all 16, every template page renders with
// working links + images, and the ladder/trifecta/attack-tree embeds load.

import { test, expect } from "@playwright/test";
import { assertNoBrokenImages, assertNoDeadInternalLinks } from "./helpers/render.ts";

const TEMPLATES = [
  "agent-design-spec", "tool-contract-template", "eval-plan-template",
  "production-readiness-checklist", "human-in-the-loop-policy", "agent-risk-register",
  "postmortem-template", "capability-tier-ladder", "roi-framework", "agent-vendor-rfp",
  "build-vs-buy-harness", "mcp-server-governance", "prompt-injection-threat-model",
  "agent-slo-definition", "escalation-runbook",
];

test("templates index lists all 16 and has no dead links", async ({ page }) => {
  await page.goto("/templates/README.html");
  await assertNoDeadInternalLinks(page);
  await assertNoBrokenImages(page);

  const hrefs = await page.evaluate(() =>
    Array.from(document.querySelectorAll("a[href]")).map((a) => a.getAttribute("href") || ""),
  );
  // Every markdown template is linked (as .html) and the JSON schema is linked directly.
  for (const name of TEMPLATES) {
    expect(hrefs.some((h) => h.includes(`${name}.html`)), `index missing link to ${name}`).toBeTruthy();
  }
  expect(
    hrefs.some((h) => h.includes("observability-event-schema.json")),
    "index missing link to observability-event-schema.json",
  ).toBeTruthy();
});

test("every template page renders with working links and images", async ({ page }) => {
  for (const name of TEMPLATES) {
    await page.goto(`/templates/${name}.html`);
    await expect(page.locator("h1")).toHaveCount(1);
    // Uniform header present.
    await expect(page.locator("body")).toContainText("Purpose:");
    await assertNoBrokenImages(page);
    await assertNoDeadInternalLinks(page);
  }
});

test("diagram-embedding templates load their real diagrams", async ({ page }) => {
  // capability-tier-ladder embeds 09; prompt-injection-threat-model embeds 10 + 13.
  await page.goto("/templates/capability-tier-ladder.html");
  await expect(page.locator('img[src*="09-capability-tier-ladder.png"]')).toHaveCount(1);
  await assertNoBrokenImages(page);

  await page.goto("/templates/prompt-injection-threat-model.html");
  await expect(page.locator('img[src*="10-lethal-trifecta-self-assessment.png"]')).toHaveCount(1);
  await expect(page.locator('img[src*="13-mcp-threat-model-attack-tree.png"]')).toHaveCount(1);
  await assertNoBrokenImages(page);
});

test("the observability JSON schema is served and is valid JSON", async ({ page }) => {
  const resp = await page.request.get("/templates/observability-event-schema.json");
  expect(resp.ok()).toBeTruthy();
  const schema = await resp.json();
  expect(schema.title).toBe("Agent Observability Event");
  expect(Array.isArray(schema.examples)).toBeTruthy();
});
