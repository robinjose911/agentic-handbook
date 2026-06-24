// Unit test for the mock LLM provider (TS binding).
// Run: node --experimental-strip-types tools/mock-llm/index.test.ts

import assert from "node:assert/strict";
import { MockProvider, MissingFixtureError, hashRequest } from "./index.ts";

const recorded = {
  system: "You are a support triage assistant. Reply with one label.",
  messages: [{ role: "user", content: "My card was declined at checkout." }],
  tools: [],
};

let failures = 0;
function test(name: string, fn: () => void) {
  try {
    fn();
    console.log(`  ok  ${name}`);
  } catch (err) {
    failures++;
    console.error(`FAIL  ${name}\n      ${(err as Error).message}`);
  }
}

test("recorded fixture returns the exact canned completion", () => {
  const resp = new MockProvider().complete(recorded);
  assert.equal(resp.content, "billing");
  assert.equal(resp.stop_reason, "end_turn");
});

test("an unrecorded hash throws MissingFixtureError", () => {
  assert.throws(
    () => new MockProvider().complete({ ...recorded, system: "drifted prompt" }),
    MissingFixtureError,
  );
});

test("identical inputs hash byte-identically across runs (determinism guard)", () => {
  assert.equal(hashRequest(recorded), hashRequest(structuredClone(recorded)));
  // Key order in the request object must not change the hash.
  const reordered = { tools: [], messages: recorded.messages, system: recorded.system };
  assert.equal(hashRequest(recorded), hashRequest(reordered));
});

test("two complete() calls return deep-equal responses", () => {
  const p = new MockProvider();
  assert.deepEqual(p.complete(recorded), p.complete(recorded));
});

test("integer-valued floats hash the same as ints (cross-language parity)", () => {
  const withFloat = { ...recorded, tools: [{ name: "f", schema: { multipleOf: 1.0 } }] };
  const withInt = { ...recorded, tools: [{ name: "f", schema: { multipleOf: 1 } }] };
  assert.equal(hashRequest(withFloat), hashRequest(withInt));
});

test("out-of-range numbers are rejected (symmetric with python)", () => {
  for (const bad of [NaN, Infinity, -Infinity, 2 ** 53, 1e21]) {
    assert.throws(() => hashRequest({ ...recorded, tools: [{ n: bad }] }));
  }
});

if (failures) {
  console.error(`\n${failures} test(s) failed`);
  process.exit(1);
}
console.log("\nall mock-llm unit tests passed");
