// Backbone render-check assertions reused by every stage spec.
//
//   assertNoBrokenImages(page)        every <img> has naturalWidth > 0
//   assertNoDeadInternalLinks(page)   every relative <a> resolves to a real page + (if present) #anchor
//   assertTableRows(page, sel, n)     a table has exactly n data rows

import { expect, type Page } from "@playwright/test";
import { classifyHref } from "./urls.ts";

export async function assertNoBrokenImages(page: Page): Promise<void> {
  // Wait until every image has settled (complete flips true on load *or* error).
  await page
    .waitForFunction(() => Array.from(document.images).every((img) => img.complete), null, {
      timeout: 10000,
    })
    .catch(() => {});
  const broken = await page.evaluate(() =>
    Array.from(document.images)
      // External images (e.g. shields.io badges, incl. protocol-relative //host) can't be verified
      // offline and aren't the repo's asset — only assert LOCAL images resolve.
      .filter((img) => !/^(https?:)?\/\//i.test(img.getAttribute("src") || ""))
      .filter((img) => !(img.naturalWidth > 0))
      .map((img) => img.getAttribute("src") || "(no src)"),
  );
  expect(broken, `broken local images on ${page.url()}: ${broken.join(", ")}`).toEqual([]);
}

export async function assertNoDeadInternalLinks(page: Page): Promise<void> {
  const base = page.url();
  const hrefs = await page.evaluate(() =>
    Array.from(document.querySelectorAll("a[href]")).map((a) => a.getAttribute("href")),
  );
  const dead: string[] = [];
  // De-dupe identical hrefs so repeated nav links are fetched once.
  for (const href of [...new Set(hrefs)]) {
    const c = classifyHref(href, base);
    if (c.kind !== "internal") continue;
    const resp = await page.request.get(c.targetUrl);
    if (!resp.ok()) {
      dead.push(`${href} -> HTTP ${resp.status()}`);
      continue;
    }
    if (c.anchor) {
      const body = await resp.text();
      // markdown-it-anchor emits id="slug" on headings.
      if (!body.includes(`id="${c.anchor}"`) && !body.includes(`name="${c.anchor}"`)) {
        dead.push(`${href} -> missing #${c.anchor}`);
      }
    }
  }
  expect(dead, `dead internal links on ${base}:\n  ${dead.join("\n  ")}`).toEqual([]);
}

export async function assertTableRows(page: Page, selector: string, n: number): Promise<void> {
  const rows = await page.locator(`${selector} tbody tr`).count();
  expect(rows, `expected ${n} data rows in ${selector}, found ${rows}`).toBe(n);
}
