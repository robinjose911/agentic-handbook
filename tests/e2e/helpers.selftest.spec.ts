// Self-test for the render-check helpers: a fixture page with one good + one broken image must
// pass / fail correctly. Uses page.setContent so it needs no files in the preview.

import { test, expect } from "@playwright/test";
import { assertNoBrokenImages } from "./helpers/render.ts";

// 1x1 transparent PNG as a data URI — always loads.
const GOOD =
  "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+M8AAAMBAQDJ/pLvAAAAAElFTkSuQmCC";

test("assertNoBrokenImages passes when every image loads", async ({ page }) => {
  await page.setContent(`<img src="${GOOD}"><img src="${GOOD}">`);
  await assertNoBrokenImages(page);
});

test("assertNoBrokenImages fails when an image is broken", async ({ page }) => {
  await page.setContent(`<img src="${GOOD}"><img src="/does-not-exist-xyz.png">`);
  let threw = false;
  try {
    await assertNoBrokenImages(page);
  } catch {
    threw = true;
  }
  expect(threw, "expected assertNoBrokenImages to throw on a broken image").toBe(true);
});
