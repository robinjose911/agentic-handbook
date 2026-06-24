# Mock LLM provider

A deterministic, offline mock LLM provider shared by every runnable example. It returns **canned,
hash-keyed responses** — no API key, no network — so the examples run reproducibly in CI and a
re-run is a no-op diff.

## How it works

`complete(request)` hashes the canonical `(system, messages, tools)` of the request to a SHA-256 and
returns the response recorded under `fixtures/<hash>.json`. An **unrecorded** request throws
(`MissingFixtureError` / `MissingFixture`) so a drifted prompt fails loudly instead of silently
hitting a real API.

The TypeScript binding (`index.ts`) and the Python binding (`mock_llm.py`) compute a **byte-identical**
canonical hash, so a single `fixtures/<hash>.json` works for both languages. Numbers must be finite and
within ±2^53; both bindings reject out-of-range values identically (never a silent cross-language split).

## Bindings

- **TypeScript:** `import { MockProvider, record } from "../../../tools/mock-llm/index.ts"` (runs under
  `node --experimental-strip-types`).
- **Python:** add `tools/mock-llm` to `sys.path`, then `import mock_llm` →
  `mock_llm.MockProvider(fixtures_dir)`, `mock_llm.record(req, resp, fixtures_dir)`.

## Recording fixtures

`record(request, response, fixturesDir)` writes a fixture in the shared canonical form. Recording is a
build-time step (off in CI); each example ships a `record-fixtures.{ts,py}` that regenerates its
fixtures from the golden set.

The cross-language hash parity is pinned by `parity-corpus.json` + `tools/validate/test_hash_parity.py`.
