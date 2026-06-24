// Print the TS-binding hash of every request in parity-corpus.json, one per line. The Python parity
// gate (tools/validate/test_hash_parity.py) shells out to this and asserts the hashes match its own,
// so any future drift between the two hand-kept canonicalizers fails a test instead of silently
// splitting the fixture namespace.
//
// Run: node --experimental-strip-types tools/mock-llm/hash_corpus.mjs

import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { hashRequest } from "./index.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const corpus = JSON.parse(readFileSync(path.join(here, "parity-corpus.json"), "utf-8"));
for (const req of corpus) console.log(hashRequest(req));
