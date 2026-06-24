import { defineConfig, devices } from "@playwright/test";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(__dirname, "..", "..");
const PORT = Number(process.env.PREVIEW_PORT || 4321);

// globalSetup regenerates placeholders + builds the preview so the render-check is self-contained.
export default defineConfig({
  testDir: __dirname,
  globalSetup: path.join(__dirname, "globalSetup.ts"),
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: 0,
  reporter: process.env.CI ? "line" : [["list"]],
  use: {
    baseURL: `http://localhost:${PORT}`,
    trace: "off",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: {
    command: `node ${path.join(REPO, "tools", "preview", "serve.mjs")}`,
    url: `http://localhost:${PORT}/README.html`,
    reuseExistingServer: !process.env.CI,
    timeout: 30_000,
    env: { PREVIEW_PORT: String(PORT) },
  },
});
