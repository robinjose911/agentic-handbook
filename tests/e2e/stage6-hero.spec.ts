// Stage 6 integration test: the README hero renders fully — banner, badges, the AGENTIC block, the
// three buttons, the decision-tree CTA — and the board PDFs resolve.

import { test, expect } from "@playwright/test";
import { assertNoBrokenImages, assertNoDeadInternalLinks } from "./helpers/render.ts";

test("README hero renders with banner, AGENTIC, ladder, and no dead links", async ({ page }) => {
  await page.goto("/README.html");
  await expect(page.locator("h1")).toHaveText("agentic-handbook");

  // The real banner asset loads (1280-wide); local images aren't broken.
  const banner = page.locator('img[src="assets/banner.png"]');
  await expect(banner).toHaveCount(1);
  const naturalWidth = await banner.evaluate((img) => (img as HTMLImageElement).naturalWidth);
  expect(naturalWidth).toBe(1280);
  await assertNoBrokenImages(page);
  await assertNoDeadInternalLinks(page);

  const body = await page.locator("body").innerText();
  for (const s of ["Autonomy", "Goals", "Evaluation", "Networks", "Trust", "Identity", "Cost"]) {
    expect(body, `AGENTIC block missing ${s}`).toContain(s);
  }
  // The capability-ladder summary renders.
  for (const tier of ["L0", "L4", "prohibited", "high-risk"]) expect(body).toContain(tier);
});

test("the three hero buttons + the decision-tree CTA link to the right places", async ({ page }) => {
  await page.goto("/README.html");
  const hrefs = await page.evaluate(() =>
    Array.from(document.querySelectorAll("a[href]")).map((a) => a.getAttribute("href") || ""),
  );
  for (const target of [
    "03-pattern-catalog", // Learn the patterns
    "templates/README", // Grab a template
    "examples/README", // See one run
    "02-decision-framework", // decision-tree CTA
  ]) {
    expect(hrefs.some((h) => h.includes(target)), `hero missing link to ${target}`).toBeTruthy();
  }
  // At least three shields.io badges are present (external, not load-checked offline).
  expect(await page.locator('img[src^="https://img.shields.io"]').count()).toBeGreaterThanOrEqual(3);
});

test("the three board PDFs resolve and are served as PDF", async ({ page }) => {
  for (const pdf of ["capability-tier-ladder", "rfp-template", "eu-ai-act-architecture"]) {
    const resp = await page.request.get(`/presentations/${pdf}.pdf`);
    expect(resp.ok(), `${pdf}.pdf should resolve`).toBeTruthy();
    expect(resp.headers()["content-type"]).toContain("pdf");
  }
});
