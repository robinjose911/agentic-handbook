// Deterministic mock LLM provider (TypeScript binding).
//
// `complete(request)` hashes the canonical (system, messages, tools) of the request and returns the
// canned response recorded under a `fixtures/` directory. An unrecorded hash throws so a drifting
// prompt fails loudly instead of silently hitting a real API. No network, no API key.
//
// The canonical JSON is byte-for-byte identical to the Python binding (mock_llm.py) so one
// `fixtures/<hash>.json` works for both languages.

import { createHash } from "node:crypto";
import { readFileSync, existsSync, mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
export const DEFAULT_FIXTURES = path.join(HERE, "fixtures");

export interface ChatMessage {
  role: string;
  content: unknown;
}
export interface CompletionRequest {
  system?: string;
  messages?: ChatMessage[];
  tools?: unknown[];
  [k: string]: unknown;
}
export interface CompletionResponse {
  content: unknown;
  stop_reason?: string;
  usage?: { input_tokens?: number; output_tokens?: number };
  [k: string]: unknown;
}

// Numbers must be finite and within the range where JS and Python serialize identically (see
// _normalize in mock_llm.py). Both bindings reject the same out-of-range numbers, so a request either
// hashes identically in both languages or fails loudly in both — never a silent cross-language split.
const MAX_SAFE = 2 ** 53;

// Stable, sorted-key JSON matching Python's json.dumps(sort_keys=True, separators=(',',':')).
function canonical(value: unknown): string {
  if (value === null || value === undefined) return "null";
  if (typeof value === "number") {
    if (!Number.isFinite(value)) throw new Error(`non-finite number ${value} cannot be canonicalized`);
    if (Math.abs(value) >= MAX_SAFE) {
      throw new Error(`number ${value} is outside the canonicalizable range (|n| < 2**53)`);
    }
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) return "[" + value.map(canonical).join(",") + "]";
  if (typeof value === "object") {
    const obj = value as Record<string, unknown>;
    const keys = Object.keys(obj).sort();
    return "{" + keys.map((k) => JSON.stringify(k) + ":" + canonical(obj[k])).join(",") + "}";
  }
  return JSON.stringify(value);
}

function canonicalRequest(request: CompletionRequest): string {
  return canonical({
    system: request.system ?? "",
    messages: request.messages ?? [],
    tools: request.tools ?? [],
  });
}

export function hashRequest(request: CompletionRequest): string {
  return createHash("sha256").update(canonicalRequest(request), "utf-8").digest("hex");
}

export class MissingFixtureError extends Error {}

export class MockProvider {
  fixturesDir: string;
  constructor(fixturesDir: string = DEFAULT_FIXTURES) {
    this.fixturesDir = fixturesDir;
  }
  complete(request: CompletionRequest): CompletionResponse {
    const digest = hashRequest(request);
    const file = path.join(this.fixturesDir, `${digest}.json`);
    if (!existsSync(file)) {
      throw new MissingFixtureError(
        `no fixture for request hash ${digest} in ${this.fixturesDir}. ` +
          `The prompt may have drifted; re-record the fixture.`,
      );
    }
    return JSON.parse(readFileSync(file, "utf-8")).response;
  }
}

// Author a fixture (off in CI). Writes the same canonical form as the Python binding (sorted keys,
// no spaces, integer-valued floats normalized) so a fixture re-recorded by either binding is
// byte-identical — the no-op-diff rule holds regardless of which language recorded it.
export function record(
  request: CompletionRequest,
  response: CompletionResponse,
  fixturesDir: string = DEFAULT_FIXTURES,
): string {
  mkdirSync(fixturesDir, { recursive: true });
  const digest = hashRequest(request);
  const file = path.join(fixturesDir, `${digest}.json`);
  writeFileSync(file, canonical({ request, response }), "utf-8");
  return file;
}
