// Unit test for the preview render harness. Run: node tools/preview/test_build.mjs
// Asserts the tiny fixture from the plan renders with a resolvable <img> and a rewritten <a>.

import assert from "node:assert/strict";
import path from "node:path";
import { renderMarkdown, build, REPO, DIST, slugify } from "./build.mjs";
import { promises as fs } from "node:fs";

let failures = 0;
async function test(name, fn) {
  try {
    await fn();
    console.log(`  ok  ${name}`);
  } catch (err) {
    failures++;
    console.error(`FAIL  ${name}\n      ${err.message}`);
  }
}

// 1. The plan's canonical fixture.
await test("renders fixture with resolvable img + rewritten .md link", async () => {
  const src = path.join(REPO, "fixture.md");
  const html = await renderMarkdown("# Hi ![x](a.png) [l](b.md)", src);
  assert.match(html, /<img[^>]+src="a\.png"/, "image src should pass through unchanged");
  assert.match(html, /<a[^>]+href="\.\/b\.html"/, ".md link should be rewritten to .html");
});

// 2. Anchor + heading slug.
await test("emits github-style heading slug", async () => {
  const html = await renderMarkdown("## What this is **not**", path.join(REPO, "x.md"));
  assert.match(html, /id="what-this-is-not"/, "heading should get a github-style id");
});

await test("slugify strips punctuation and lowercases", () => {
  assert.equal(slugify("L0–L4 Mapping!"), "l0l4-mapping");
});

await test("slugify preserves non-ASCII letters (matches github anchors)", () => {
  // GitHub keeps accented letters in the slug; an ASCII-only slugify would drop them and break links.
  assert.equal(slugify("Café Setup"), "café-setup");
  assert.equal(slugify("Łódź Notes"), "łódź-notes");
});

await test("slugify does not collapse double spaces (github double-hyphen)", () => {
  // Removing the `/` leaves two spaces -> two hyphens, exactly like github.com. Collapsing would
  // make the preview pass a link that 404s on the real site.
  assert.equal(slugify("Build / test commands"), "build--test-commands");
});

// 3. Directory link resolves to README.html when the dir has a README.
await test("rewrites directory link to README.html when a README exists", async () => {
  // assets/diagrams/ has a README.md, so a link to it resolves to its rendered README.
  const html = await renderMarkdown("[d](assets/diagrams/)", path.join(REPO, "README.md"));
  assert.match(html, /href="\.\/assets\/diagrams\/README\.html"/);
});

// 3b. Directory link without a README is left unchanged (and warns) rather than becoming a dead link.
await test("leaves a directory link without a README unchanged", async () => {
  // assets/images/ holds only assets (no README.md); the link must not be rewritten to a dead one.
  const html = await renderMarkdown("[i](assets/images/)", path.join(REPO, "README.md"));
  assert.match(html, /href="assets\/images\/"/);
  assert.doesNotMatch(html, /assets\/images\/README\.html/);
});

// 4. External + anchor links are left alone.
await test("leaves external and pure-anchor links unchanged", async () => {
  const html = await renderMarkdown("[e](https://x.com) [a](#top)", path.join(REPO, "x.md"));
  assert.match(html, /href="https:\/\/x\.com"/);
  assert.match(html, /href="#top"/);
});

// 5. Full build produces README.html and copies the banner asset.
await test("full build emits README.html and copies an asset", async () => {
  await build();
  await fs.stat(path.join(DIST, "README.html"));
  await fs.stat(path.join(DIST, "assets", "banner.png"));
});

if (failures) {
  console.error(`\n${failures} test(s) failed`);
  process.exit(1);
}
console.log("\nall preview unit tests passed");
