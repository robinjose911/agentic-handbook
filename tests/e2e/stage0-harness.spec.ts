// Stage 0 integration test: the empty-but-stubbed repo renders with zero broken images and zero
// dead internal links. The README skeleton and the placeholder-bearing diagram gallery both load.

import { test, expect } from "@playwright/test";
import { assertNoBrokenImages, assertNoDeadInternalLinks } from "./helpers/render.ts";

test("README skeleton renders with title, banner placeholder, and no dead links", async ({ page }) => {
  await page.goto("/README.html");
  await expect(page.locator("h1")).toHaveText("agentic-handbook");
  // The banner placeholder image resolves.
  const banner = page.locator('img[src="assets/banner.png"]');
  await expect(banner).toHaveCount(1);
  await assertNoBrokenImages(page);
  await assertNoDeadInternalLinks(page);
});

test("diagram gallery shows 15 placeholder diagrams, none broken", async ({ page }) => {
  await page.goto("/assets/diagrams/README.html");
  const imgs = page.locator("table img");
  await expect(imgs).toHaveCount(15);
  await assertNoBrokenImages(page);
  await assertNoDeadInternalLinks(page);
});

test("a git-ignored CLAUDE.md is absent from the published preview", async ({ page }) => {
  const resp = await page.request.get("/CLAUDE.html");
  expect(resp.status()).toBe(404);
});
