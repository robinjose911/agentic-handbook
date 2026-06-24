// Record step (OFF in CI). Authors the canned mock-provider fixtures from the golden set so the
// example runs offline. Re-run only when the prompt or the golden inputs change:
//
//   node --experimental-strip-types record-fixtures.ts
//
// There is no real-provider call here — the canned classifications are the golden labels, which is
// what makes the run deterministic and the eval a test of the routing logic, not the model.

import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { record } from "../../../tools/mock-llm/index.ts";
import { classifyRequest } from "./src/agent.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const golden = JSON.parse(readFileSync(path.join(here, "eval", "golden.json"), "utf-8"));
const fixturesDir = path.join(here, "fixtures");

let n = 0;
for (const g of golden) {
  const req = classifyRequest({ id: g.id, text: g.text });
  const resp = {
    content: JSON.stringify({ intent: g.expectedIntent, urgency: g.urgency }),
    stop_reason: "end_turn",
    usage: { input_tokens: 22, output_tokens: 6 },
  };
  record(req, resp, fixturesDir);
  n++;
}
console.log(`recorded ${n} fixtures into ${path.relative(here, fixturesDir)}/`);
