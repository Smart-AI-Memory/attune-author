"""Tests for attune_author.preamble."""

from __future__ import annotations

from pathlib import Path

import pytest

from attune_author.preamble import (
    _extract_preamble,
    get_preamble,
    get_related_preambles,
)


class TestExtractPreamble:
    """Tests for _extract_preamble()."""

    def test_extracts_first_paragraph(self) -> None:
        """Test extracting the first non-heading line."""
        text = (
            "---\n"
            "feature: foo\n"
            "---\n"
            "\n"
            "# Foo Title\n"
            "\n"
            "Use foo when you need bar.\n"
            "\n"
            "More content here.\n"
        )
        assert _extract_preamble(text) == "Use foo when you need bar."

    def test_skips_frontmatter(self) -> None:
        """Test that frontmatter is skipped."""
        text = "---\n" "key: value\n" "---\n" "First line.\n"
        assert _extract_preamble(text) == "First line."

    def test_skips_headings(self) -> None:
        """Test that headings are skipped."""
        text = "---\n" "---\n" "# Heading 1\n" "## Heading 2\n" "Real content.\n"
        assert _extract_preamble(text) == "Real content."

    def test_returns_none_for_empty(self) -> None:
        """Test None for content with no extractable preamble."""
        text = "---\n---\n\n# Only Heading\n"
        assert _extract_preamble(text) is None

    def test_no_frontmatter(self) -> None:
        """Test extraction when there's no frontmatter."""
        text = "First line.\n"
        assert _extract_preamble(text) == "First line."

    def test_frontmatter_without_closing_marker(self) -> None:
        """A malformed template with an opening ``---`` but
        no closing marker must not hang or crash. The body
        parser should still fall back to something sensible
        (returning None is the documented empty-state).
        """
        text = "---\nkey: value\nno closing marker ever follows\n"
        # The extractor does not deadlock and yields a result
        # (None or a string) — the contract is that it
        # returns cleanly.
        result = _extract_preamble(text)
        assert result is None or isinstance(result, str)

    def test_frontmatter_only_no_body(self) -> None:
        """A file with only frontmatter and no body returns None."""
        text = "---\nkey: value\n---\n"
        assert _extract_preamble(text) is None

    def test_only_headings_no_body(self) -> None:
        """A body made entirely of headings returns None."""
        text = "---\n---\n# Top\n## Sub\n### Deeper\n"
        assert _extract_preamble(text) is None


class TestGetPreambleEdgeCases:
    """Error-path tests for get_preamble()."""

    def test_non_utf8_file_returns_none(self, tmp_path: Path) -> None:
        """A task.md with non-UTF-8 bytes must not crash —
        the reader swallows UnicodeDecodeError via the
        OSError path or similar and returns None.
        """
        help_dir = tmp_path / ".help"
        tpl_dir = help_dir / "templates" / "bad"
        tpl_dir.mkdir(parents=True)
        # Latin-1 bytes that are not valid UTF-8.
        (tpl_dir / "task.md").write_bytes(b"\xff\xfe\xfd not valid utf-8")

        from attune_author.preamble import get_preamble

        # Current behavior: may raise UnicodeDecodeError or
        # return None. This test pins the "must not crash
        # the caller" contract. If UnicodeDecodeError leaks,
        # this test fails and we add the appropriate catch
        # in preamble.py.
        try:
            result = get_preamble("bad", help_dir)
        except UnicodeDecodeError:
            pytest.fail("get_preamble leaked UnicodeDecodeError")
        assert result is None or isinstance(result, str)


class TestGetPreamble:
    """Tests for get_preamble()."""

    def test_reads_task_template(self, tmp_path: Path) -> None:
        """Test reading preamble from a task template."""
        help_dir = tmp_path / ".help"
        tpl_dir = help_dir / "templates" / "auth"
        tpl_dir.mkdir(parents=True)

        (tpl_dir / "task.md").write_text(
            "---\nfeature: auth\n---\n\n# Auth Tasks\n\n"
            "Use auth when you need to verify users.\n",
            encoding="utf-8",
        )

        result = get_preamble("auth", help_dir)
        assert result == "Use auth when you need to verify users."

    def test_returns_none_for_missing_template(self, tmp_path: Path) -> None:
        """Test None when task template doesn't exist."""
        help_dir = tmp_path / ".help"
        help_dir.mkdir()
        assert get_preamble("nonexistent", help_dir) is None

    def test_rejects_path_traversal(self, tmp_path: Path) -> None:
        """Test that path traversal in feature name is blocked."""
        help_dir = tmp_path / ".help"
        help_dir.mkdir()

        for bad_name in ["../etc", "foo/bar", "test\x00null", ""]:
            assert get_preamble(bad_name, help_dir) is None

    def test_default_help_dir(self, tmp_path: Path, monkeypatch) -> None:
        """Test that .help/ in cwd is the default."""
        monkeypatch.chdir(tmp_path)
        tpl_dir = tmp_path / ".help" / "templates" / "foo"
        tpl_dir.mkdir(parents=True)
        (tpl_dir / "task.md").write_text("---\n---\nUse foo for stuff.\n", encoding="utf-8")

        assert get_preamble("foo") == "Use foo for stuff."


class TestGetRelatedPreambles:
    """Tests for get_related_preambles()."""

    def test_finds_related_by_tags(self, tmp_path: Path) -> None:
        """Test finding features related by shared tags."""
        help_dir = tmp_path / ".help"
        help_dir.mkdir()

        # Create manifest with tagged features
        (help_dir / "features.yaml").write_text(
            "version: 1\n"
            "features:\n"
            "  auth:\n"
            "    description: Auth\n"
            "    tags: [security, users]\n"
            "  permissions:\n"
            "    description: Permissions\n"
            "    tags: [security, access]\n"
            "  unrelated:\n"
            "    description: Other\n"
            "    tags: [misc]\n",
            encoding="utf-8",
        )

        # Create task templates with preambles
        for feat in ["permissions"]:
            tpl_dir = help_dir / "templates" / feat
            tpl_dir.mkdir(parents=True)
            (tpl_dir / "task.md").write_text(
                f"---\n---\nUse {feat} when needed.\n",
                encoding="utf-8",
            )

        results = get_related_preambles("auth", help_dir)

        assert len(results) >= 1
        feat_names = [r["feature"] for r in results]
        assert "permissions" in feat_names
        assert "unrelated" not in feat_names

    def test_returns_empty_for_no_manifest(self, tmp_path: Path) -> None:
        """Test empty list when manifest doesn't exist."""
        help_dir = tmp_path / ".help"
        help_dir.mkdir()
        assert get_related_preambles("foo", help_dir) == []

    def test_returns_empty_for_no_tags(self, tmp_path: Path) -> None:
        """Test empty list when feature has no tags."""
        help_dir = tmp_path / ".help"
        help_dir.mkdir()
        (help_dir / "features.yaml").write_text(
            "version: 1\nfeatures:\n  foo:\n    description: Foo\n",
            encoding="utf-8",
        )
        assert get_related_preambles("foo", help_dir) == []

    def test_rejects_path_traversal(self, tmp_path: Path) -> None:
        """Test path traversal protection."""
        help_dir = tmp_path / ".help"
        help_dir.mkdir()
        for bad in ["../etc", "foo/bar", "x\x00y", ""]:
            assert get_related_preambles(bad, help_dir) == []
