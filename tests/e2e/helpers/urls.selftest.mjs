// Browser-free unit test for the dead-link URL classifier.
// Run: node --experimental-strip-types tests/e2e/helpers/urls.selftest.mjs

import assert from "node:assert/strict";
import { classifyHref } from "./urls.ts";

const BASE = "http://localhost:4321/docs/00-introduction.html";

let failures = 0;
function test(name, fn) {
  try {
    fn();
    console.log(`  ok  ${name}`);
  } catch (err) {
    failures++;
    console.error(`FAIL  ${name}\n      ${err.message}`);
  }
}

test("external http link is external", () => {
  assert.equal(classifyHref("https://anthropic.com", BASE).kind, "external");
});

test("mailto is external", () => {
  assert.equal(classifyHref("mailto:x@y.com", BASE).kind, "external");
});

test("relative .html link is internal with resolved absolute url", () => {
  const c = classifyHref("../templates/README.html", BASE);
  assert.equal(c.kind, "internal");
  assert.equal(c.targetUrl, "http://localhost:4321/templates/README.html");
  assert.equal(c.anchor, "");
});

test("relative link with anchor captures the anchor", () => {
  const c = classifyHref("02-decision-framework.html#what-this-is-not", BASE);
  assert.equal(c.kind, "internal");
  assert.equal(c.targetUrl, "http://localhost:4321/docs/02-decision-framework.html");
  assert.equal(c.anchor, "what-this-is-not");
});

test("same-page anchor is internal, points at current page", () => {
  const c = classifyHref("#section", BASE);
  assert.equal(c.kind, "internal");
  assert.equal(c.targetUrl, BASE);
  assert.equal(c.anchor, "section");
});

test("bare hash is skipped", () => {
  assert.equal(classifyHref("#", BASE).kind, "skip");
});

test("null/empty href is skipped", () => {
  assert.equal(classifyHref(null, BASE).kind, "skip");
  assert.equal(classifyHref("", BASE).kind, "skip");
});

if (failures) {
  console.error(`\n${failures} test(s) failed`);
  process.exit(1);
}
console.log("\nall url-classifier unit tests passed");
