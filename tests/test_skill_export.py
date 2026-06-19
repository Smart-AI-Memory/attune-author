"""Tests for ``attune_author.skill_export``.

Each test stages a small fixture corpus under ``tmp_path`` to keep the
test independent of the bundled attune-help corpus shape.
"""

from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

import pytest

from attune_author.skill_export import (
    ExportResult,
    _canonical_slug,
    _first_paragraph_summary,
    export_skills,
)


def _write_template(root: Path, kind: str, slug: str, body: str = "") -> Path:
    target = root / kind / f"{slug}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body or _default_body(slug), encoding="utf-8")
    return target


def _default_body(slug: str) -> str:
    return dedent(
        f"""\
        ---
        type: concept
        name: {slug}
        tags: [test]
        ---

        # {slug.replace('-', ' ').title()}

        {slug.replace('-', ' ').capitalize()} is a feature that does an
        interesting thing for the test corpus.

        ## What

        It works.
        """
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class TestCanonicalSlug:
    def test_strips_tool_prefix(self) -> None:
        assert _canonical_slug("tool-security-audit") == "security-audit"

    def test_strips_task_prefix(self) -> None:
        assert _canonical_slug("task-error-handling-design") == "error-handling-design"

    def test_leaves_un_prefixed_slug(self) -> None:
        assert _canonical_slug("audience-adaptation") == "audience-adaptation"


class TestFirstParagraphSummary:
    def test_returns_first_sentence(self) -> None:
        body = "# Heading\n\nThis is the first sentence. And this is the second."
        assert _first_paragraph_summary(body) == "This is the first sentence."

    def test_skips_headings(self) -> None:
        body = "# H1\n## H2\n\nReal text starts here. Continues."
        assert _first_paragraph_summary(body) == "Real text starts here."

    def test_returns_none_when_only_headings(self) -> None:
        body = "# Title\n\n## Subhead\n"
        assert _first_paragraph_summary(body) is None

    def test_truncates_overlong_paragraph(self) -> None:
        body = "# H\n\n" + ("x" * 250)
        out = _first_paragraph_summary(body, max_chars=200)
        assert out is not None
        assert len(out) == 200
        assert out.endswith("…")


# ---------------------------------------------------------------------------
# export_skills happy path
# ---------------------------------------------------------------------------


@pytest.fixture
def corpus(tmp_path: Path) -> Path:
    (tmp_path / "summaries.json").write_text(
        json.dumps(
            {
                "security-audit": "Scans for vulnerabilities.",
                "audience-adaptation": "Renders help differently per channel.",
            }
        ),
        encoding="utf-8",
    )
    _write_template(tmp_path, "concepts", "tool-security-audit")
    _write_template(tmp_path, "concepts", "audience-adaptation")
    _write_template(tmp_path, "concepts", "task-debugging-sessions")
    return tmp_path


def test_writes_one_skill_per_concept(corpus: Path, tmp_path: Path) -> None:
    out = tmp_path / "skills"
    result = export_skills(corpus, out)

    written_features = sorted(r.feature for r in result.written)
    assert written_features == ["audience-adaptation", "debugging-sessions", "security-audit"]
    assert result.skipped == []


def test_skill_md_contains_summary_description(corpus: Path, tmp_path: Path) -> None:
    out = tmp_path / "skills"
    export_skills(corpus, out)
    skill = (out / "security-audit" / "SKILL.md").read_text(encoding="utf-8")
    assert "name: security-audit" in skill
    assert "Scans for vulnerabilities." in skill


def test_skill_md_falls_back_to_first_paragraph_when_no_summary(
    corpus: Path, tmp_path: Path
) -> None:
    out = tmp_path / "skills"
    export_skills(corpus, out)
    skill = (out / "debugging-sessions" / "SKILL.md").read_text(encoding="utf-8")
    # No summary entry exists for debugging-sessions; expect extracted prose.
    assert "is a feature that does an interesting thing" in skill


def test_canonical_slug_used_for_output_dir(corpus: Path, tmp_path: Path) -> None:
    out = tmp_path / "skills"
    export_skills(corpus, out)
    # tool-security-audit.md → security-audit/SKILL.md
    assert (out / "security-audit" / "SKILL.md").exists()
    assert not (out / "tool-security-audit").exists()


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_missing_concepts_dir_returns_empty(tmp_path: Path) -> None:
    result = export_skills(tmp_path, tmp_path / "skills")
    assert result.written == []
    assert result.skipped == []


def test_empty_concept_body_is_skipped(tmp_path: Path) -> None:
    (tmp_path / "concepts").mkdir()
    (tmp_path / "concepts" / "empty.md").write_text("---\ntype: concept\n---\n\n", encoding="utf-8")
    result = export_skills(tmp_path, tmp_path / "skills")
    assert result.written == []
    assert result.skipped == [("empty", "empty concept body")]


def test_unsafe_slug_is_skipped(tmp_path: Path) -> None:
    concepts = tmp_path / "concepts"
    concepts.mkdir()
    (concepts / "Bad Slug.md").write_text("---\n---\nhi", encoding="utf-8")
    result = export_skills(tmp_path, tmp_path / "skills")
    assert any(reason == "unsafe slug" for _, reason in result.skipped)


def test_existing_skill_is_skipped_without_overwrite(corpus: Path, tmp_path: Path) -> None:
    out = tmp_path / "skills"
    export_skills(corpus, out)  # first pass writes
    result = export_skills(corpus, out)  # second pass skips
    assert result.written == []
    assert all("exists" in reason for _, reason in result.skipped)


def test_overwrite_replaces_existing(corpus: Path, tmp_path: Path) -> None:
    out = tmp_path / "skills"
    export_skills(corpus, out)
    skill_path = out / "security-audit" / "SKILL.md"
    skill_path.write_text("# stale", encoding="utf-8")
    result = export_skills(corpus, out, overwrite=True)
    assert any(r.feature == "security-audit" for r in result.written)
    assert "name: security-audit" in skill_path.read_text(encoding="utf-8")


def test_summaries_json_missing_uses_extracted_descriptions(tmp_path: Path) -> None:
    """No summaries.json at all — every description comes from body extraction."""
    _write_template(tmp_path, "concepts", "alpha")
    out = tmp_path / "skills"
    result = export_skills(tmp_path, out)
    assert len(result.written) == 1
    skill = (out / "alpha" / "SKILL.md").read_text(encoding="utf-8")
    assert "alpha is a feature" in skill.lower()


def test_export_result_dataclass_initialises_empty() -> None:
    """The dataclass with default factories shouldn't share state across instances."""
    a = ExportResult()
    b = ExportResult()
    a.written.append(None)  # type: ignore[arg-type]
    assert b.written == []
