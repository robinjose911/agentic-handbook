// Stage 4 integration test: the shipped AI-native files are served and their internal links resolve;
// the git-ignored CLAUDE.md is absent from the published preview.

import { test, expect } from "@playwright/test";
import { assertNoDeadInternalLinks } from "./helpers/render.ts";

test("llms.txt is served and lists chapters + templates", async ({ page }) => {
  const resp = await page.request.get("/llms.txt");
  expect(resp.ok()).toBeTruthy();
  const body = await resp.text();
  expect(body).toContain("docs/00-introduction.md");
  expect(body).toContain("templates/agent-design-spec.md");
  expect(body).toContain("templates/observability-event-schema.json");
});

test("AGENTS.md renders with no dead internal links", async ({ page }) => {
  await page.goto("/AGENTS.html");
  await expect(page.locator("h1")).toContainText("AGENTS.md");
  await assertNoDeadInternalLinks(page);
});

test("the .github instruction tree renders with resolving links", async ({ page }) => {
  for (const path of [
    "/.github/copilot-instructions.html",
    "/.github/instructions/docs.instructions.html",
    "/.github/instructions/examples.instructions.html",
    "/.github/instructions/diagrams.instructions.html",
  ]) {
    const resp = await page.goto(path); // goto's response proves it is served — one round-trip, not two
    expect(resp?.ok(), `${path} should be served`).toBeTruthy();
    await assertNoDeadInternalLinks(page);
  }
});

test("the git-ignored CLAUDE.md is absent from the published preview", async ({ page }) => {
  const resp = await page.request.get("/CLAUDE.html");
  expect(resp.status()).toBe(404);
});
