"""Doc-discipline tests: keep the entry file thin and the doc graph intact.

This is the lightweight doc-freshness guard referenced by the harness — it
fails the build if CLAUDE.md bloats past its budget or any markdown relative
link dangles.
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"
MAX_CLAUDE_LINES = 120

# Governance docs that must remain reachable from the entry map.
GOVERNANCE_LINKS = [
    "docs/index.md",
    "ARCHITECTURE.md",
    "DECISIONS.md",
    "ROADMAP.md",
    "TASKS.md",
    "MEMORY.md",
]

_LINK_RE = re.compile(r"\]\(([^)]+)\)")


def _markdown_files() -> list[Path]:
    return [p for p in REPO_ROOT.rglob("*.md") if ".venv" not in p.parts]


def test_claude_md_is_thin() -> None:
    """CLAUDE.md is a map, not a monolith (KS-0005)."""
    line_count = len(CLAUDE_MD.read_text(encoding="utf-8").splitlines())
    assert line_count <= MAX_CLAUDE_LINES, (
        f"CLAUDE.md is {line_count} lines (budget {MAX_CLAUDE_LINES}); "
        "push depth into doc/."
    )


def test_claude_md_links_governance_docs() -> None:
    """The entry map must link to every governance doc — no orphans (KS-0005)."""
    text = CLAUDE_MD.read_text(encoding="utf-8")
    missing = [link for link in GOVERNANCE_LINKS if f"({link})" not in text]
    assert not missing, f"CLAUDE.md is missing links to: {missing}"


def test_no_broken_relative_links() -> None:
    """Every relative markdown link must resolve to a real file (KS-0005)."""
    broken: list[str] = []
    for md in _markdown_files():
        for match in _LINK_RE.finditer(md.read_text(encoding="utf-8")):
            link = match.group(1).split("#")[0].strip()
            if not link or link.startswith(("http://", "https://", "mailto:")):
                continue
            if not (md.parent / link).resolve().exists():
                broken.append(f"{md.relative_to(REPO_ROOT)} -> {link}")
    assert not broken, "broken relative links:\n" + "\n".join(broken)
