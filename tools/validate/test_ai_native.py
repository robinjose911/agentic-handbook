"""Validator: the shipped AI-native files reference only real paths and real commands (Stage 4)."""
import json
import os
import re

import pytest

import catalog  # noqa: E402 (same dir)

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

ROOT_FILES = ["llms.txt", "AGENTS.md"]
GITHUB_FILES = [
    ".github/copilot-instructions.md",
    ".github/instructions/docs.instructions.md",
    ".github/instructions/examples.instructions.md",
    ".github/instructions/diagrams.instructions.md",
]
ALL_AI_NATIVE = ROOT_FILES + GITHUB_FILES

CHAPTERS = catalog.CHAPTERS
TEMPLATES = catalog.TEMPLATES_ALL

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
# Inline-code paths that look like repo paths (start with a known top dir or end in a known ext).
CODE_PATH_RE = re.compile(
    r"`((?:tools|tests|docs|templates|assets|examples|\.github)/[^`\s]+|[^`\s]+\.(?:py|mjs|ts|json|md|yml))`"
)


def _read(rel: str) -> str:
    with open(os.path.join(REPO, rel), encoding="utf-8") as fh:
        return fh.read()


def _strip_code(text: str) -> str:
    """Remove fenced + inline code so illustrative `[x](path)` examples in code aren't checked as
    real navigation links. (Trade-off: a real link placed inside a code span is not checked — keep
    real navigation links out of code spans.)"""
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"`[^`]*`", "", text)
    return text


def _slugify(s: str) -> str:
    # Mirrors tools/preview/build.mjs slugify (GitHub-style): lowercase, strip punctuation, each
    # space -> a hyphen (no run-collapse). Used to validate in-page anchors at the unit layer.
    s = re.sub(r"[^\w\- ]+", "", s.lower())
    return s.replace(" ", "-")


def _valid_anchors(md_path: str) -> set:
    with open(md_path, encoding="utf-8") as fh:
        text = fh.read()
    anchors = set(re.findall(r'<a id="([^"]+)"></a>', text))  # explicit <a id> anchors
    for m in re.finditer(r"^#{1,6}\s+(.*)$", text, flags=re.MULTILINE):  # heading slugs
        anchors.add(_slugify(m.group(1).strip()))
    return anchors


@pytest.mark.parametrize("rel", ALL_AI_NATIVE)
def test_ai_native_file_exists(rel):
    assert os.path.exists(os.path.join(REPO, rel)), f"missing AI-native file: {rel}"


@pytest.mark.parametrize("rel", ALL_AI_NATIVE)
def test_markdown_links_resolve_to_real_paths(rel):
    text = _strip_code(_read(rel))
    base = os.path.dirname(os.path.join(REPO, rel))
    for target in LINK_RE.findall(text):
        if re.match(r"^(https?:|mailto:|#)", target):
            continue
        path, _, anchor = target.partition("#")
        if not path:
            continue
        resolved = os.path.normpath(os.path.join(base, path))
        assert os.path.exists(resolved), f"{rel}: link target does not resolve: {target}"
        # If the link carries an anchor into a markdown file, that anchor must exist (no dangling
        # in-page link) — the same guarantee the e2e dead-link check enforces, at the unit layer.
        if anchor and resolved.endswith(".md"):
            assert anchor in _valid_anchors(resolved), (
                f"{rel}: link {target} points at a missing anchor #{anchor}"
            )


@pytest.mark.parametrize("rel", ALL_AI_NATIVE)
def test_inline_code_paths_resolve(rel):
    text = _read(rel)
    base = os.path.dirname(os.path.join(REPO, rel))
    for m in CODE_PATH_RE.finditer(text):
        cand = m.group(1)
        # Only check repo-relative-looking paths (skip bare command words / globs).
        if "/" not in cand or "*" in cand or " " in cand:
            continue
        # Resolve deterministically by form: a `../`-prefixed path is file-relative, otherwise it is
        # repo-relative. (Avoids a dead repo-relative path being rescued by a coincidental subtree.)
        root = base if cand.startswith(("..", "./")) else REPO
        resolved = os.path.normpath(os.path.join(root, cand))
        assert os.path.exists(resolved), f"{rel}: inline path does not exist: {cand}"


def test_llms_txt_lists_all_chapters_and_templates():
    text = _read("llms.txt")
    for slug in CHAPTERS:
        assert f"docs/{slug}.md" in text, f"llms.txt missing chapter path docs/{slug}.md"
    for name in TEMPLATES:
        ext = "json" if name == "observability-event-schema" else "md"
        assert f"templates/{name}.{ext}" in text, f"llms.txt missing template path templates/{name}.{ext}"


def test_agents_md_commands_reference_real_files():
    text = _read("AGENTS.md")
    for path in ["tools/validate/all.py", "tools/preview/build.mjs", "tools/preview/serve.mjs", "tests/e2e"]:
        assert path in text, f"AGENTS.md should document the real command path {path}"
        assert os.path.exists(os.path.join(REPO, path)), f"AGENTS.md references missing {path}"
    # `npm --prefix tests/e2e test` must map to a real `test` script.
    if "npm --prefix tests/e2e test" in text:
        with open(os.path.join(REPO, "tests", "e2e", "package.json"), encoding="utf-8") as fh:
            scripts = json.load(fh).get("scripts", {})
        assert "test" in scripts, "AGENTS.md documents `npm --prefix tests/e2e test` but no test script exists"


def test_ai_native_files_carry_the_canonical_mnemonic():
    # AGENTS.md, llms.txt, and copilot-instructions.md each restate the AGENTIC surfaces; guard them
    # against repo.config.json so a surface rename can't leave a shipped file out of sync (rule #4).
    with open(os.path.join(REPO, "repo.config.json"), encoding="utf-8") as fh:
        surfaces = [s["name"] for s in json.load(fh)["mnemonic"]["surfaces"]]
    for rel in ["AGENTS.md", "llms.txt", ".github/copilot-instructions.md"]:
        text = _read(rel)
        for name in surfaces:
            assert name in text, f"{rel} is missing canonical AGENTIC surface '{name}'"
