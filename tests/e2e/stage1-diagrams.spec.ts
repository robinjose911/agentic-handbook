// Stage 1 integration test: the diagram gallery shows all 15 real diagrams at their manifest sizes,
// none broken, and zero placeholder diagram slots remain.

import { test, expect } from "@playwright/test";
import { assertNoBrokenImages, assertNoDeadInternalLinks } from "./helpers/render.ts";

test("gallery renders 15 real diagrams at their manifest dimensions", async ({ page }) => {
  // Load the manifest the build copies into the preview.
  const manifestResp = await page.request.get("/assets/manifest.json");
  expect(manifestResp.ok()).toBeTruthy();
  const manifest = await manifestResp.json();
  const diagrams = new Map<string, { width: number; height: number; status: string }>(
    manifest.slots
      .filter((s: any) => s.kind === "diagram")
      .map((s: any) => [s.id, { width: s.width, height: s.height, status: s.status }]),
  );
  expect(diagrams.size).toBe(15);

  // No diagram slot may still be a placeholder.
  const placeholders = [...diagrams.entries()].filter(([, v]) => v.status !== "real").map(([k]) => k);
  expect(placeholders, `placeholder diagram slots: ${placeholders.join(", ")}`).toEqual([]);

  await page.goto("/assets/diagrams/README.html");
  const imgs = page.locator("table img");
  await expect(imgs).toHaveCount(15);
  await assertNoBrokenImages(page);
  await assertNoDeadInternalLinks(page);

  // Each rendered image's natural size must equal the manifest's recorded size for its slot id.
  const rendered = await page.evaluate(() =>
    Array.from(document.querySelectorAll("table img")).map((el) => {
      const img = el as HTMLImageElement;
      const src = img.getAttribute("src") || "";
      return { id: src.replace(/\.png$/, ""), w: img.naturalWidth, h: img.naturalHeight };
    }),
  );
  for (const r of rendered) {
    const slot = diagrams.get(r.id);
    expect(slot, `gallery image ${r.id} has no manifest slot`).toBeTruthy();
    expect(r.w, `${r.id} width`).toBe(slot!.width);
    expect(r.h, `${r.id} height`).toBe(slot!.height);
  }
});
