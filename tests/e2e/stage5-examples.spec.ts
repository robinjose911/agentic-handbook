// Stage 5 integration test: the examples index lists exactly 5 runnable examples; each example page
// renders with resolvable artifact links + the synthetic/teaching label; 05 carries the medical frame.

import { test, expect } from "@playwright/test";
import { assertNoBrokenImages, assertNoDeadInternalLinks, assertTableRows } from "./helpers/render.ts";

const EXAMPLES = [
  "typescript/01-support-triage-agent",
  "typescript/02-outbound-lead-workflow-agent",
  "typescript/03-evaluator-optimizer-self-improving",
  "python/04-research-synthesis-multi-agent",
  "python/05-healthcare-intake-regulated-domain",
];

test("examples index lists exactly 5 runnable examples with working links", async ({ page }) => {
  await page.goto("/examples/README.html");
  await assertTableRows(page, "table", 5);
  await assertNoDeadInternalLinks(page);
  const hrefs = await page.evaluate(() =>
    Array.from(document.querySelectorAll("a[href]")).map((a) => a.getAttribute("href") || ""),
  );
  for (const ex of EXAMPLES) {
    expect(hrefs.some((h) => h.includes(ex)), `index missing example ${ex}`).toBeTruthy();
  }
});

test("every example page renders with resolvable artifacts and the teaching label", async ({ page }) => {
  for (const ex of EXAMPLES) {
    await page.goto(`/examples/${ex}/README.html`);
    await expect(page.locator("h1")).toHaveCount(1);
    await assertNoBrokenImages(page);
    await assertNoDeadInternalLinks(page); // checks the trace/eval/receipt artifact links too

    const body = (await page.locator("body").innerText()).toLowerCase();
    expect(body, `${ex} must carry a synthetic/teaching label`).toMatch(/synthetic|teaching/);

    // The committed receipts must be served.
    for (const artifact of ["trace.jsonl", "eval-report.json", "receipt.json"]) {
      const resp = await page.request.get(`/examples/${ex}/${artifact}`);
      expect(resp.ok(), `${ex}/${artifact} should resolve`).toBeTruthy();
    }
  }
});

test("the healthcare example carries the 'not medical advice' frame", async ({ page }) => {
  await page.goto("/examples/python/05-healthcare-intake-regulated-domain/README.html");
  const body = (await page.locator("body").innerText()).toLowerCase();
  expect(body).toContain("not medical advice");
});
