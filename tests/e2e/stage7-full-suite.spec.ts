// Stage 7 capstone: visit EVERY rendered page in the preview (enumerated from dist, not just the
// pages reachable from the README) and assert none has a broken local image or a dead internal link.
// Enumerating from disk means an orphan page (on disk but unlinked) is still checked. Plus launch-safety.

import { test, expect } from "@playwright/test";
import { promises as fs } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { assertNoBrokenImages, assertNoDeadInternalLinks } from "./helpers/render.ts";

const DIST = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..", "tools", "preview", "dist");

async function htmlPages(dir: string, base = DIST): Promise<string[]> {
  const out: string[] = [];
  for (const e of await fs.readdir(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) out.push(...(await htmlPages(p, base)));
    else if (e.name.endsWith(".html")) out.push("/" + path.relative(base, p).split(path.sep).join("/"));
  }
  return out;
}

test("every rendered page in the repo: no broken images, no dead internal links", async ({ page }) => {
  test.setTimeout(180_000);
  const pages = await htmlPages(DIST);
  expect(pages.length, "the build should render many pages").toBeGreaterThan(50);

  for (const url of pages) {
    const resp = await page.goto(url);
    expect(resp?.ok(), `${url} should be served`).toBeTruthy();
    await assertNoBrokenImages(page);
    await assertNoDeadInternalLinks(page);
  }
});

test("the README is intact (not empty) and shows the AGENTIC hero", async ({ page }) => {
  await page.goto("/README.html");
  await expect(page.locator("h1")).toHaveText("agentic-handbook");
  const body = await page.locator("body").innerText();
  expect(body.length).toBeGreaterThan(800);
  for (const s of ["Autonomy", "Goals", "Evaluation", "Networks", "Trust", "Identity", "Cost"]) {
    expect(body).toContain(s);
  }
});

test("git-ignored build context is absent from the published preview", async ({ page }) => {
  for (const path of ["/CLAUDE.html", "/samples/launch-copy.html", "/samples/agentic-handbook-plan.html"]) {
    expect((await page.request.get(path)).status(), `${path} must not be published`).toBe(404);
  }
});
