"""Validator (Stage 7.1): repo-wide internal-link integrity (every relative markdown link/image
resolves on disk, directory links have a README), and every external URL is allowlisted or well-formed.
Live external 200-checking is a network step left for Robin / CI (see allowlist.json)."""
import glob
import json
import os
import re

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
# Mirror build.mjs's ignore set so the validator only checks files the renderer actually publishes.
IGNORE_DIRS = {
    "node_modules", "dist", ".venv", "venv", "samples", ".claude", ".git", "test-results",
    "playwright-report", ".playwright", "__pycache__", ".pytest_cache",
}
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
ALLOWLIST = os.path.join(REPO, "tools", "links", "allowlist.json")


def _slugify(s: str) -> str:
    # Mirrors tools/preview/build.mjs slugify (github-style).
    return re.sub(r"[^\w\- ]+", "", s.lower()).replace(" ", "-")


def _valid_anchors(md_path: str) -> set:
    with open(md_path, encoding="utf-8") as fh:
        text = fh.read()
    anchors = set(re.findall(r'<a id="([^"]+)"></a>', text))
    for m in re.finditer(r"^#{1,6}\s+(.*)$", text, flags=re.MULTILINE):
        anchors.add(_slugify(m.group(1).strip()))
    return anchors


IGNORE_FILES = {"CLAUDE.md"}  # git-ignored build context — not shipped, not scanned


def _md_files():
    out = []
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in files:
            if f.endswith(".md") and f not in IGNORE_FILES:
                out.append(os.path.join(root, f))
    return out


def _resolve_internal(src_file: str, target: str) -> tuple[bool, str]:
    """Return (ok, detail) for a relative link target, mirroring build.mjs resolution + anchor check."""
    # Strip an optional markdown link title: [x](path "Title") -> path.
    target = re.sub(r"""\s+["'].*$""", "", target.strip())
    path, _, anchor = target.partition("#")
    base = os.path.dirname(src_file)
    if not path:  # same-page anchor
        target_md = src_file
    else:
        resolved = os.path.normpath(os.path.join(base, path))
        if os.path.isdir(resolved) or path.endswith("/"):
            readme = os.path.join(resolved, "README.md")
            return (os.path.exists(readme), readme)  # directory link -> its README (repo convention)
        if not os.path.exists(resolved):
            return False, resolved
        target_md = resolved if resolved.endswith(".md") else None
    # Validate the anchor against the target markdown file's headings + <a id> anchors.
    if anchor and target_md and os.path.exists(target_md):
        if anchor not in _valid_anchors(target_md):
            return False, f"{target} (missing #{anchor})"
    return True, target


def test_no_dead_internal_links_repo_wide():
    dead = []
    for src in _md_files():
        with open(src, encoding="utf-8") as fh:
            text = fh.read()
        # Skip fenced + inline code so illustrative `[x](path#<id>)` examples aren't checked as links.
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        text = re.sub(r"`[^`]*`", "", text)
        for target in LINK_RE.findall(text):
            if re.match(r"^(https?:|mailto:|tel:|data:|#|//)", target):
                continue
            ok, resolved = _resolve_internal(src, target)
            if not ok:
                dead.append(f"{os.path.relpath(src, REPO)} -> {target}")
    assert not dead, "dead internal links:\n  " + "\n  ".join(dead)


def test_external_urls_are_allowlisted_or_well_formed():
    with open(ALLOWLIST, encoding="utf-8") as fh:
        allow = [a["pattern"] for a in json.load(fh)["allow"]]
    bad = []
    for src in _md_files() + [os.path.join(REPO, "references.md")]:
        if not os.path.exists(src):
            continue
        with open(src, encoding="utf-8") as fh:
            for url in re.findall(r"https?://[^\s)\"'>]+", fh.read()):
                url = url.rstrip(".,`'\"")  # strip trailing prose punctuation
                # Well-formed = scheme + a host with a dot, or localhost. (Live 200-check = Robin/CI.)
                well_formed = (
                    re.match(r"^https?://[^/\s]+\.[^/\s]+", url) is not None
                    or url.startswith("http://localhost")
                )
                allowed = any(url.startswith(p) for p in allow)
                if not (well_formed or allowed):
                    bad.append(f"{os.path.relpath(src, REPO)} -> {url}")
    assert not bad, "malformed external URLs:\n  " + "\n  ".join(bad)
