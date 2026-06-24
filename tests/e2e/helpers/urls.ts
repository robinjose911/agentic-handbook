// Pure URL-classification logic for the dead-link checker. No Playwright import, so it is unit-
// testable in plain Node (helpers/urls.selftest.mjs).

export type HrefKind = "external" | "skip" | "internal";

export interface ClassifiedHref {
  kind: HrefKind;
  targetUrl: string; // absolute URL to fetch (internal only)
  anchor: string; // fragment id without '#', or ''
}

const EXTERNAL = /^(https?:|mailto:|tel:|data:|\/\/)/i;

export function classifyHref(href: string | null, baseUrl: string): ClassifiedHref {
  const empty: ClassifiedHref = { kind: "skip", targetUrl: "", anchor: "" };
  if (!href) return empty;
  if (EXTERNAL.test(href)) return { kind: "external", targetUrl: href, anchor: "" };

  const base = new URL(baseUrl);
  const url = new URL(href, baseUrl);
  if (url.origin !== base.origin) return { kind: "external", targetUrl: url.href, anchor: "" };

  const anchor = url.hash ? decodeURIComponent(url.hash.slice(1)) : "";
  // A bare "#" (no anchor) pointing at the current page is a no-op link, skip it.
  if (!url.pathname && !anchor) return empty;
  if (href === "#") return empty;

  const targetUrl = url.origin + url.pathname + url.search;
  return { kind: "internal", targetUrl, anchor };
}
