"""Cross-repo contract: ``attune-author status`` output ⇄ attune-ai parser.

attune-ai's dashboard shells out to ``attune-author status`` and parses
the markdown to learn which help features are stale
(``attune-ai/src/attune/ops/help_data.py::_parse_status_output``). The
two repos can't import each other, so this test pins the contract from
attune-author's side: if ``format_status_report`` ever changes shape in
a way that breaks the parser, THIS repo's CI goes red (spec task 1.6,
constraint C2).

The parser below is a faithful copy of attune-ai's as of 2026-06-14.
If attune-ai's parser changes, update this mirror in lockstep.
"""

from __future__ import annotations

import re
from pathlib import Path

from attune_author.maintenance import format_status_report
from attune_author.staleness import DocStaleness, FeatureStaleness, StalenessReport

# --- Mirror of attune-ai/src/attune/ops/help_data.py (do not drift) ------

_TABLE_ROW_RE = re.compile(r"^\s*\|\s*([a-z][a-z0-9-]*)\s*\|")


def _attune_ai_parse_status_output(text: str) -> frozenset[str]:
    """Faithful copy of attune-ai's ``_parse_status_output``.

    Collects stale feature slugs ONLY from the ``### Stale`` table under
    ``## Help Templates`` — ``## Project Docs`` stale rows are ignored
    (the dashboard's "regenerate" can't fix docs/).
    """
    out: set[str] = set()
    in_project_docs = False
    in_stale = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            in_project_docs = "Project Docs" in stripped
            in_stale = False
            continue
        if stripped.startswith("###"):
            in_stale = stripped == "### Stale"
            continue
        if not in_stale or in_project_docs:
            continue
        m = _TABLE_ROW_RE.match(line)
        if m:
            out.add(m.group(1))
    return frozenset(out)


# --- The contract -------------------------------------------------------


def _report() -> StalenessReport:
    return StalenessReport(
        help_entries=[
            FeatureStaleness("auth", True, "h-new", None, ["a.py", "b.py"]),
            FeatureStaleness("cli", False, "h-same", "h-same", ["c.py"]),
        ],
        doc_entries=[
            DocStaleness(
                feature="docs-only-feature",
                doc_path="docs/how-to/x.md",
                kind="how-to",
                is_stale=True,
                missing=False,
                current_hash="h-doc",
            )
        ],
    )


def test_parser_extracts_only_help_stale_features(tmp_path: Path) -> None:
    # tmp_path as help_dir: no task templates -> empty preambles, no
    # accidental pickup of the worktree's real .help corpus.
    out = format_status_report(_report(), help_dir=tmp_path)
    parsed = _attune_ai_parse_status_output(out)

    assert parsed == frozenset({"auth"})  # stale help feature only
    assert "cli" not in parsed  # current is not stale
    assert "docs-only-feature" not in parsed  # Project Docs excluded


def test_structural_anchors_present(tmp_path: Path) -> None:
    out = format_status_report(_report(), help_dir=tmp_path)
    # The exact tokens the parser keys on.
    assert "## Help Templates" in out
    assert "### Stale" in out
    assert "## Project Docs" in out
    # Stale feature row: feature slug is the FIRST table column.
    assert re.search(r"^\s*\|\s*auth\s*\|", out, re.MULTILINE)


def test_table_header_and_divider_are_not_parsed_as_features(
    tmp_path: Path,
) -> None:
    # The "| Feature | Description |..." header and "|----|" divider must
    # not match _TABLE_ROW_RE (they don't start with a lowercase slug).
    out = format_status_report(_report(), help_dir=tmp_path)
    parsed = _attune_ai_parse_status_output(out)
    assert "feature" not in parsed
