// Static server for the rendered preview. Serves `tools/preview/dist/` on http://localhost:4321.
// Resolves `/` and directory URLs to README.html (GitHub behaviour) so internal links work.

import { createServer } from "node:http";
import { promises as fs } from "node:fs";
import { createReadStream } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { MIME } from "./extensions.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DIST = path.join(__dirname, "dist");
const PORT = Number(process.env.PREVIEW_PORT || 4321);

async function resolveFile(urlPath) {
  let rel = decodeURIComponent(urlPath.split("?")[0]).replace(/^\/+/, "");
  let target = path.resolve(DIST, rel);
  // Block path traversal: target must resolve to a path inside DIST (a real boundary check, not a
  // lexical prefix that a sibling like `dist-evil` could satisfy).
  const within = path.relative(DIST, target);
  if (within === ".." || within.startsWith(".." + path.sep) || path.isAbsolute(within)) return null;

  try {
    const st = await fs.stat(target);
    if (st.isDirectory()) target = path.join(target, "README.html");
  } catch {
    // Not a direct hit. If it has no extension, try `.html` (rendered markdown).
    if (!path.extname(target)) {
      const asHtml = target + ".html";
      try {
        await fs.stat(asHtml);
        target = asHtml;
      } catch {
        return null;
      }
    } else {
      return null;
    }
  }
  try {
    await fs.stat(target);
    return target;
  } catch {
    return null;
  }
}

const server = createServer(async (req, res) => {
  let urlPath = req.url || "/";
  if (urlPath === "/" || urlPath === "") urlPath = "/README.html";
  const file = await resolveFile(urlPath);
  if (!file) {
    res.writeHead(404, { "content-type": "text/plain" });
    res.end(`404 Not Found: ${req.url}`);
    return;
  }
  const ext = path.extname(file).toLowerCase();
  res.writeHead(200, { "content-type": MIME[ext] || "application/octet-stream" });
  createReadStream(file).pipe(res);
});

server.listen(PORT, () => {
  console.log(`preview serving ${DIST} at http://localhost:${PORT}`);
});
