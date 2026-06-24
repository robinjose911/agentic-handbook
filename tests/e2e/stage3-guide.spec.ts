// Stage 3 integration test: every guide chapter renders with working images, links, and citation
// anchors; the foundation chapters embed the hero; ch12 carries the ladder table; ch01 the mnemonic.

import { test, expect } from "@playwright/test";
import { assertNoBrokenImages, assertNoDeadInternalLinks } from "./helpers/render.ts";

const CHAPTERS = [
  "00-introduction", "01-mnemonic-and-systems-map", "02-decision-framework", "03-pattern-catalog",
  "04-tool-design-and-contracts", "05-memory-state-and-durable-execution",
  "06-protocol-stack-skills-mcp-a2a", "07-codeact-vs-tool-calls", "08-computer-use-and-browser-agents",
  "09-model-selection-for-roles", "10-agent-identity-and-auth", "11-security-and-threat-model",
  "12-eu-ai-act-as-architecture", "13-evaluations", "14-observability-lite", "15-cost-stack",
  "16-production-readiness", "17-anti-patterns", "18-case-studies",
];

test("the guide index lists all 19 chapters and resolves", async ({ page }) => {
  await page.goto("/docs/README.html");
  await assertNoDeadInternalLinks(page);
  const hrefs = await page.evaluate(() =>
    Array.from(document.querySelectorAll("a[href]")).map((a) => a.getAttribute("href") || ""),
  );
  for (const slug of CHAPTERS) {
    expect(hrefs.some((h) => h.includes(`${slug}.html`)), `index missing ${slug}`).toBeTruthy();
  }
});

test("every chapter renders with working images, links, and citation anchors", async ({ page }) => {
  for (const slug of CHAPTERS) {
    await page.goto(`/docs/${slug}.html`);
    await expect(page.locator("h1")).toHaveCount(1);
    await assertNoBrokenImages(page);
    await assertNoDeadInternalLinks(page); // also checks every references.md#id anchor exists
  }
});

test("foundation chapters embed the hero; ch11/ch12 embed their diagrams", async ({ page }) => {
  for (const slug of ["00-introduction", "01-mnemonic-and-systems-map", "02-decision-framework"]) {
    await page.goto(`/docs/${slug}.html`);
    await expect(page.locator('img[src*="00-hero-decision-tree.png"]')).toHaveCount(1);
  }
  await page.goto("/docs/11-security-and-threat-model.html");
  await expect(page.locator('img[src*="10-lethal-trifecta-self-assessment.png"]')).toHaveCount(1);
  await page.goto("/docs/12-eu-ai-act-as-architecture.html");
  await expect(page.locator('img[src*="09-capability-tier-ladder.png"]')).toHaveCount(1);
});

test("ch01 renders the full AGENTIC mnemonic table", async ({ page }) => {
  await page.goto("/docs/01-mnemonic-and-systems-map.html");
  const body = await page.locator("body").innerText();
  for (const surface of ["Autonomy", "Goals", "Evaluation", "Networks", "Trust", "Identity", "Cost"]) {
    expect(body).toContain(surface);
  }
});

test("ch12 renders the capability-ladder table with all five tiers", async ({ page }) => {
  await page.goto("/docs/12-eu-ai-act-as-architecture.html");
  const body = await page.locator("body").innerText();
  for (const tier of ["L0", "L1", "L2", "L3", "L4", "prohibited", "high-risk"]) {
    expect(body).toContain(tier);
  }
});
