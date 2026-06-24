// Single source of previewable file types. build.mjs copies these files through to dist; serve.mjs
// serves them with the right content-type. One table keeps the copied set and the served set from
// drifting apart (a copy/serve split-brain where a file is present but downloaded, or served but 404s).

export const MIME = {
  ".html": "text/html; charset=utf-8",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".gif": "image/gif",
  ".svg": "image/svg+xml",
  ".webp": "image/webp",
  ".pdf": "application/pdf",
  ".json": "application/json",
  ".jsonl": "application/x-ndjson",
  ".txt": "text/plain; charset=utf-8",
  ".csv": "text/csv; charset=utf-8",
  ".mmd": "text/plain; charset=utf-8",
  ".ts": "text/plain; charset=utf-8",
  ".tsx": "text/plain; charset=utf-8",
  ".js": "text/plain; charset=utf-8",
  ".mjs": "text/plain; charset=utf-8",
  ".py": "text/plain; charset=utf-8",
  ".yml": "text/plain; charset=utf-8",
  ".yaml": "text/plain; charset=utf-8",
  ".toml": "text/plain; charset=utf-8",
  ".env": "text/plain; charset=utf-8",
};

// Files copied verbatim into the preview: every previewable type except generated `.html`
// (rendered from markdown by build.mjs, never copied).
export const COPY_EXT = new Set(Object.keys(MIME).filter((ext) => ext !== ".html"));
