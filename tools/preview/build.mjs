// Local preview render harness.
//
// Renders every Markdown file in the repo to GitHub-flavoured HTML, rewrites relative `.md` links to
// their rendered `.html` form (resolving directory links to README.html the way GitHub does), and
// copies every other file (images, JSON artifacts, llms.txt, example fixtures) through verbatim so
// `<img src>` and artifact links resolve. Output goes to `tools/preview/dist/` (git-ignored).
//
// This stands in for GitHub's renderer so the Playwright render-checks never need to push to test.

import { promises as fs } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import MarkdownIt from "markdown-it";
import anchor from "markdown-it-anchor";
import { COPY_EXT } from "./extensions.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
export const REPO = path.resolve(__dirname, "..", "..");
export const DIST = path.join(__dirname, "dist");

// Directories never rendered or copied into the preview.
const IGNORE_DIRS = new Set([
  ".git", "node_modules", "dist", ".venv", "venv", "samples", ".claude",
  "test-results", "playwright-report", ".playwright", "__pycache__", ".pytest_cache",
]);
// Files that exist on disk but are git-ignored build context — never published to the preview.
const IGNORE_FILES = new Set(["CLAUDE.md", ".DS_Store", "Thumbs.db"]);

// GitHub-style heading slugifier, matching github-slugger: lowercase, strip punctuation (keep
// letters/numbers/underscore/hyphen in any script — é, ł, … — so anchors match github.com), then
// replace EACH remaining space with a hyphen. Crucially this does NOT collapse runs of spaces:
// "Build / test commands" -> "build--test-commands" (the `/` is removed, leaving two spaces -> two
// hyphens), exactly as github.com renders it. Collapsing would silently diverge from the real site.
export function slugify(s) {
  return String(s)
    .toLowerCase()
    .replace(/[^\p{L}\p{N}_\- ]+/gu, "")
    .replace(/ /g, "-");
}

const md = new MarkdownIt({ html: true, linkify: true, typographer: false }).use(anchor, {
  slugify,
  permalink: anchor.permalink.headerLink({ safariReaderFix: true }),
});

async function walk(dir, acc = []) {
  for (const entry of await fs.readdir(dir, { withFileTypes: true })) {
    if (entry.isDirectory()) {
      if (IGNORE_DIRS.has(entry.name)) continue;
      await walk(path.join(dir, entry.name), acc);
    } else if (entry.isFile()) {
      if (IGNORE_FILES.has(entry.name)) continue;
      acc.push(path.join(dir, entry.name));
    }
  }
  return acc;
}

async function isDir(p) {
  try {
    return (await fs.stat(p)).isDirectory();
  } catch {
    return false;
  }
}

async function exists(p) {
  try {
    await fs.stat(p);
    return true;
  } catch {
    return false;
  }
}

// Rewrite a relative href found in `srcFile` (absolute path) for the rendered preview.
async function rewriteHref(href, srcFile) {
  if (!href) return href;
  if (/^(https?:|mailto:|tel:|data:|#|\/\/)/i.test(href)) return href; // external / pure-anchor
  const [rawPath, ...rest] = href.split("#");
  const anchorPart = rest.length ? "#" + rest.join("#") : "";
  if (rawPath === "") return href; // pure anchor like "#foo"

  const srcDir = path.dirname(srcFile);
  let target = path.resolve(srcDir, rawPath);

  // Directory link -> its README (GitHub behaviour), but only when the README actually exists.
  // Otherwise leave the link untouched and warn at build time, so a missing README surfaces here
  // instead of silently becoming a dead `.html` link the render-check only catches later.
  if (rawPath.endsWith("/") || (await isDir(target))) {
    const readme = path.join(target, "README.md");
    if (!(await exists(readme))) {
      console.warn(
        `[preview] directory link "${href}" in ${path.relative(REPO, srcFile)} has no README.md`,
      );
      return href;
    }
    target = readme;
  }
  if (target.endsWith(".md")) {
    const rel = path.relative(REPO, target).replace(/\.md$/, ".html");
    return relFromSrc(srcFile, rel) + anchorPart;
  }
  return href; // non-md relative link (image, artifact) is copied through verbatim
}

// Express a repo-relative dist path as a link relative to the source file's rendered location.
function relFromSrc(srcFile, repoRelTarget) {
  const srcRel = path.relative(REPO, srcFile).replace(/\.md$/, ".html");
  const fromDir = path.dirname(srcRel);
  let r = path.relative(fromDir, repoRelTarget);
  if (!r.startsWith(".")) r = "./" + r;
  return r.split(path.sep).join("/");
}

function pageHtml(title, body) {
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${title}</title>
<style>
  :root { color-scheme: light; }
  body { box-sizing: border-box; margin: 0 auto; max-width: 980px; padding: 32px 24px 96px;
    font: 16px/1.6 -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    color: #1f2328; }
  h1, h2, h3, h4 { line-height: 1.25; margin: 24px 0 16px; }
  h1 { font-size: 2em; border-bottom: 1px solid #d1d9e0; padding-bottom: .3em; }
  h2 { font-size: 1.5em; border-bottom: 1px solid #d1d9e0; padding-bottom: .3em; }
  a { color: #0969da; text-decoration: none; }
  a:hover { text-decoration: underline; }
  code { background: #eff1f3; border-radius: 6px; padding: .2em .4em; font-size: 85%;
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
  pre { background: #f6f8fa; border-radius: 6px; padding: 16px; overflow: auto; }
  pre code { background: transparent; padding: 0; }
  table { border-collapse: collapse; display: block; overflow: auto; margin: 16px 0; }
  th, td { border: 1px solid #d1d9e0; padding: 6px 13px; }
  tr:nth-child(2n) { background: #f6f8fa; }
  img { max-width: 100%; box-sizing: content-box; }
  blockquote { color: #59636e; border-left: .25em solid #d1d9e0; padding: 0 1em; margin: 0 0 16px; }
  .header-anchor { float: left; margin-left: -20px; padding-right: 4px; opacity: 0; }
  h1:hover .header-anchor, h2:hover .header-anchor, h3:hover .header-anchor { opacity: 1; }
</style>
</head>
<body>
${body}
</body>
</html>
`;
}

// Render a markdown string to body HTML, rewriting relative links as if it lived at `srcFile`.
export async function renderMarkdown(raw, srcFile) {
  const env = {};
  const tokens = md.parse(raw, env);
  for (const tok of tokens) {
    if (tok.type === "inline" && tok.children) {
      for (const child of tok.children) {
        if (child.type === "link_open") {
          const hrefIndex = child.attrIndex("href");
          if (hrefIndex >= 0) {
            child.attrs[hrefIndex][1] = await rewriteHref(child.attrs[hrefIndex][1], srcFile);
          }
        }
      }
    }
  }
  return md.renderer.render(tokens, md.options, env);
}

export async function build() {
  await fs.rm(DIST, { recursive: true, force: true });
  await fs.mkdir(DIST, { recursive: true });

  const files = await walk(REPO);
  for (const file of files) {
    const rel = path.relative(REPO, file);
    const ext = path.extname(file).toLowerCase();

    if (ext === ".md") {
      const raw = await fs.readFile(file, "utf-8");
      const body = await renderMarkdown(raw, file);
      const title = (raw.match(/^#\s+(.+)$/m)?.[1] || rel).trim();
      const outPath = path.join(DIST, rel.replace(/\.md$/, ".html"));
      await fs.mkdir(path.dirname(outPath), { recursive: true });
      await fs.writeFile(outPath, pageHtml(title, body), "utf-8");
    } else if (COPY_EXT.has(ext) || ext === "") {
      const outPath = path.join(DIST, rel);
      await fs.mkdir(path.dirname(outPath), { recursive: true });
      await fs.copyFile(file, outPath);
    }
  }
  return DIST;
}

// Run when invoked directly (not when imported by the unit test).
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  build()
    .then((dist) => console.log(`preview built -> ${dist}`))
    .catch((err) => {
      console.error(err);
      process.exit(1);
    });
}
