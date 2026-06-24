"""Validator: growth + contribution scaffolding (topics, issue templates, FAQ, security, launch copy)
exists and is well-formed (Stage 7.4)."""
import os
import re
import subprocess

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

ISSUE_TEMPLATES = ["bug_report", "pattern_proposal", "anti_pattern_proposal"]


def _read(rel):
    with open(os.path.join(REPO, rel), encoding="utf-8") as fh:
        return fh.read()


def test_github_topics_has_exactly_twenty():
    lines = [ln.strip() for ln in _read(".github/topics.txt").splitlines() if ln.strip()]
    assert len(lines) == 20, f"expected 20 GitHub topics, found {len(lines)}"
    assert len(set(lines)) == 20, "duplicate topic"
    for t in lines:
        assert re.fullmatch(r"[a-z0-9-]+", t), f"invalid topic slug: {t}"


def _frontmatter(text: str):
    """Return the YAML frontmatter block (between the first two '---' fences), or None."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i]
    return None  # unclosed frontmatter


def test_issue_templates_exist_and_parse():
    for name in ISSUE_TEMPLATES:
        fm = _frontmatter(_read(f".github/ISSUE_TEMPLATE/{name}.md"))
        assert fm is not None, f"{name}: missing or unclosed YAML frontmatter (GitHub won't list it)"
        keys = {ln.split(":", 1)[0].strip() for ln in fm if ":" in ln and not ln.startswith(" ")}
        assert "name" in keys, f"{name}: frontmatter has no 'name:' key"
        assert "about" in keys, f"{name}: frontmatter has no 'about:' key"


def test_security_and_contributing_exist():
    for rel in ("SECURITY.md", "CONTRIBUTING.md"):
        assert os.path.exists(os.path.join(REPO, rel)), f"missing {rel}"


def test_faq_exists_with_questions():
    text = _read("FAQ.md")
    questions = re.findall(r"^##\s+.+\?", text, flags=re.MULTILINE)
    assert len(questions) >= 3, f"FAQ should have >=3 question sections, found {len(questions)}"


def _git_ignored(rel):
    return subprocess.run(["git", "check-ignore", rel], cwd=REPO, capture_output=True).returncode == 0


def test_launch_copy_exists_and_is_git_ignored():
    assert os.path.exists(os.path.join(REPO, "samples", "launch-copy.md")), "missing samples/launch-copy.md"
    assert _git_ignored("samples/launch-copy.md"), "launch copy must be git-ignored (under /samples)"
