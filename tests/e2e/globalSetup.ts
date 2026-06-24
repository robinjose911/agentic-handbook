// Playwright globalSetup: regenerate placeholder stubs, then build the preview, so the render-check
// is fully self-contained (a clean checkout renders green before the server boots).

import { execFileSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(__dirname, "..", "..");

function venvPython(): string {
  // Prefer the repo-local venv; fall back to python3 on PATH.
  const venv = path.join(REPO, ".venv", "bin", "python");
  return venv;
}

export default async function globalSetup() {
  // 1. Regenerate placeholders (real assets are never clobbered).
  try {
    execFileSync(venvPython(), [path.join(REPO, "tools", "stubs", "make_placeholders.py")], {
      stdio: "inherit",
    });
  } catch {
    // Fall back to python3 if the venv is absent.
    execFileSync("python3", [path.join(REPO, "tools", "stubs", "make_placeholders.py")], {
      stdio: "inherit",
    });
  }
  // 2. Build the preview.
  execFileSync("node", [path.join(REPO, "tools", "preview", "build.mjs")], { stdio: "inherit" });
}
