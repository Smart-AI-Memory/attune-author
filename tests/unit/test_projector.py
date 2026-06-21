"""Tests for the deterministic master-file projector (T2).

See ``docs/specs/help-docs-single-source/t2-projector-build.md`` in
attune-ai. The fixture mirrors attune-ai's
``content/features/spec-engine.md`` (merged in attune-ai #960) so the
test is hermetic and runnable in attune-author CI.
"""

from __future__ import annotations

from pathlib import Path

from attune_author.projector import (
    DOCS_PAGE_SECTIONS,
    HELP_FRONTMATTER_KEYS,
    HELP_KIND_SECTIONS,
    parse_master_file,
    project_feature,
)

FIXTURE = Path(__file__).parent / "fixtures" / "spec-engine.md"

#: The 10 H2 sections the spec-engine master file declares, in order.
MASTER_SECTIONS = [
    "Overview",
    "Concepts",
    "Quickstart",
    "Tasks",
    "Reference",
    "Comparison",
    "Failure modes",
    "FAQ seeds",
    "Notes & tips",
    "Design & extension",
]


def _parse_help_frontmatter(content: str) -> dict[str, str]:
    """Pull the leading ``---`` frontmatter block into a flat dict."""
    assert content.startswith("---\n")
    _, block, _ = content.split("---\n", 2)
    out: dict[str, str] = {}
    for line in block.strip().splitlines():
        key, _, value = line.partition(":")
        out[key.strip()] = value.strip()
    return out


# --- parse_master_file ------------------------------------------------------


def test_parse_master_file_yields_all_sections():
    master = parse_master_file(FIXTURE)
    assert master.feature == "spec-engine"
    assert list(master.sections.keys()) == MASTER_SECTIONS
    assert len(master.sections) == 10
    # Bodies are captured, not just headings.
    assert "spec engine" in master.sections["Overview"].lower()
    assert "| Type |" in master.sections["Concepts"]


def test_parse_ignores_h2_inside_code_fences():
    # The Tasks section is heavy with fenced python; none of its
    # in-fence lines should have spawned phantom sections.
    master = parse_master_file(FIXTURE)
    assert list(master.sections.keys()) == MASTER_SECTIONS


# --- project_feature: planning ---------------------------------------------


def test_dry_run_plans_ten_help_kinds_and_four_docs(tmp_path):
    result = project_feature(FIXTURE, tmp_path, tmp_path / ".help", dry_run=True)
    help_outputs = [o for o in result.outputs if o.target == "help"]
    docs_outputs = [o for o in result.outputs if o.target == "docs"]

    assert len(help_outputs) == 10
    assert len(docs_outputs) == 4
    assert {o.kind for o in help_outputs} == set(HELP_KIND_SECTIONS)
    assert {o.kind for o in docs_outputs} == set(DOCS_PAGE_SECTIONS)
    # faq is never planned (D7).
    assert "faq" not in {o.kind for o in help_outputs}
    # dry-run writes nothing.
    assert result.written == []
    assert not any(tmp_path.rglob("*.md"))


def test_help_frontmatter_has_seven_keys_and_depth_equals_kind(tmp_path):
    result = project_feature(FIXTURE, tmp_path, tmp_path / ".help", dry_run=True)
    for out in result.outputs:
        if out.target != "help":
            continue
        fm = _parse_help_frontmatter(out.content)
        assert set(fm) == set(HELP_FRONTMATTER_KEYS)
        assert fm["depth"] == out.kind
        assert fm["type"] == out.kind
        assert fm["name"] == f"spec-engine-{out.kind}"
        assert fm["feature"] == "spec-engine"
        assert fm["status"] == "generated"
        assert fm["source_hash"]  # non-empty


def test_docs_pages_carry_footer(tmp_path):
    result = project_feature(FIXTURE, tmp_path, tmp_path / ".help", dry_run=True)
    docs = [o for o in result.outputs if o.target == "docs"]
    assert docs
    for out in docs:
        assert "<!-- attune-generated:" in out.content
        assert "feature=spec-engine" in out.content
        assert f"kind={out.kind}" in out.content
        # No YAML frontmatter on docs pages.
        assert not out.content.startswith("---\n")


# --- project_feature: writing ----------------------------------------------


def test_project_feature_writes_to_disk(tmp_path):
    help_dir = tmp_path / ".help"
    result = project_feature(FIXTURE, tmp_path, help_dir, dry_run=False)

    assert len(result.written) == 14
    assert (help_dir / "templates" / "spec-engine" / "concept.md").exists()
    assert (help_dir / "templates" / "spec-engine" / "reference.md").exists()
    # docs land at their nav.mkdocs paths (note tutorials/ pluralization).
    assert (tmp_path / "docs" / "how-to" / "spec-engine.md").exists()
    assert (tmp_path / "docs" / "tutorials" / "spec-engine.md").exists()
    assert (tmp_path / "docs" / "architecture" / "spec-engine.md").exists()
    assert (tmp_path / "docs" / "reference" / "spec-engine.md").exists()
    # faq is never written (D7 / DD5).
    assert not (help_dir / "templates" / "spec-engine" / "faq.md").exists()


# --- tolerate missing sections ---------------------------------------------


def test_missing_section_skips_only_dependent_outputs(tmp_path):
    # A minimal master with only Overview, Concepts, and Notes & tips:
    # concept/note/tip render; every output depending on an absent
    # section is skipped — never an error.
    master = tmp_path / "tiny.md"
    master.write_text(
        "---\n"
        "feature: tiny\n"
        "summary: x\n"
        "---\n\n"
        "## Overview\n\nthe overview\n\n"
        "## Concepts\n\nthe concepts\n\n"
        "## Notes & tips\n\nthe notes\n",
        encoding="utf-8",
    )

    result = project_feature(master, tmp_path, tmp_path / ".help", dry_run=True)
    rendered = {o.kind for o in result.outputs}

    assert rendered == {"concept", "note", "tip"}
    # Dependent outputs are recorded as skipped, with the missing
    # section named.
    assert any(s.startswith("reference") for s in result.skipped)
    assert any(s.startswith("comparison") for s in result.skipped)
    assert any(s.startswith("error") for s in result.skipped)
    assert any(s.startswith("docs/how-to") for s in result.skipped)
    assert any(s.startswith("docs/tutorial") for s in result.skipped)
