"""Tests for attune_author.staleness."""

from __future__ import annotations

import logging
from pathlib import Path

from attune_author.generator import generate_feature_templates
from attune_author.manifest import Feature, load_manifest
from attune_author.staleness import (
    FeatureStaleness,
    StalenessReport,
    _read_frontmatter_value,
    check_staleness,
    compute_source_hash,
    parse_doc_footer,
)


def _write_features_yaml(help_dir: Path, body: str) -> None:
    (help_dir / "features.yaml").write_text(body, encoding="utf-8")


class TestReadFrontmatterValue:
    """Tests for _read_frontmatter_value()."""

    def test_reads_value(self) -> None:
        """Test extracting a value from frontmatter."""
        text = "---\nfoo: bar\nbaz: 123\n---\ncontent"
        assert _read_frontmatter_value(text, "foo") == "bar"
        assert _read_frontmatter_value(text, "baz") == "123"

    def test_returns_none_for_missing_key(self) -> None:
        """Test None for missing key."""
        text = "---\nfoo: bar\n---\ncontent"
        assert _read_frontmatter_value(text, "missing") is None

    def test_returns_none_without_frontmatter(self) -> None:
        """Test None for content without frontmatter."""
        assert _read_frontmatter_value("no frontmatter", "foo") is None

    def test_returns_none_for_unclosed_frontmatter(self) -> None:
        """Test None for unclosed frontmatter block."""
        assert _read_frontmatter_value("---\nfoo: bar\n", "foo") is None


class TestComputeSourceHash:
    """Tests for compute_source_hash()."""

    def test_hashes_matched_files(self, project_root: Path) -> None:
        """Test that hash is computed from matched files."""
        feature = Feature(
            name="auth",
            description="Auth",
            files=["src/auth/**"],
        )

        digest, matched = compute_source_hash(feature, project_root)

        assert len(digest) == 64  # SHA-256 hex
        assert len(matched) > 0
        assert any("login.py" in f for f in matched)

    def test_consistent_hash(self, project_root: Path) -> None:
        """Test that same files produce same hash."""
        feature = Feature(name="auth", description="", files=["src/auth/**"])

        hash1, _ = compute_source_hash(feature, project_root)
        hash2, _ = compute_source_hash(feature, project_root)

        assert hash1 == hash2

    def test_empty_for_no_matches(self, project_root: Path) -> None:
        """Test empty matched list for non-matching patterns."""
        feature = Feature(name="nope", description="", files=["nonexistent/**"])

        digest, matched = compute_source_hash(feature, project_root)

        assert matched == []
        assert len(digest) == 64  # Empty hash is still valid


class TestStalenessReport:
    """Tests for StalenessReport properties."""

    def test_stale_count(self) -> None:
        """Test stale_count property."""
        report = StalenessReport(
            help_entries=[
                FeatureStaleness("a", is_stale=True, current_hash="x", stored_hash="y"),
                FeatureStaleness("b", is_stale=False, current_hash="z", stored_hash="z"),
                FeatureStaleness("c", is_stale=True, current_hash="w", stored_hash=None),
            ]
        )

        assert report.stale_count == 2
        assert report.current_count == 1
        assert report.stale_features == ["a", "c"]


class TestCheckStaleness:
    """Tests for check_staleness()."""

    def test_all_stale_without_templates(self, help_dir: Path, project_root: Path) -> None:
        """Test that features without templates are stale."""
        manifest = load_manifest(help_dir)
        report = check_staleness(manifest, help_dir, project_root)

        # No templates exist yet, so stored hash is None -> stale
        assert report.stale_count == 2

    def test_filter_by_feature_name(self, help_dir: Path, project_root: Path) -> None:
        """Test filtering staleness check by feature name."""
        manifest = load_manifest(help_dir)
        report = check_staleness(manifest, help_dir, project_root, features=["auth"])

        assert len(report.help_entries) == 1
        assert report.help_entries[0].feature == "auth"


class TestProjectDocFooterStaleness:
    """Integration: project-doc generator writes a footer that check_staleness reads.

    Guards the round trip between ``_render_project_doc_template`` in the
    generator and ``parse_doc_footer`` / ``check_staleness`` in attune-help.
    """

    _MANIFEST = (
        "version: 1\n"
        "features:\n"
        "  auth:\n"
        "    description: Authentication and authorization\n"
        "    files: [src/auth/**]\n"
        "    doc_path: docs/how-to/auth.md\n"
    )

    def test_freshly_generated_doc_has_parseable_footer(
        self, help_dir: Path, project_root: Path
    ) -> None:
        """Generator emits an attune-generated footer that parse_doc_footer reads."""
        _write_features_yaml(help_dir, self._MANIFEST)
        manifest = load_manifest(help_dir)
        feature = manifest.features["auth"]

        generate_feature_templates(
            feature=feature,
            help_dir=help_dir,
            project_root=project_root,
            depths=["how-to"],
        )

        doc_file = project_root / "docs" / "how-to" / "auth.md"
        assert doc_file.exists()

        content = doc_file.read_text(encoding="utf-8")
        attrs = parse_doc_footer(content)
        assert attrs["feature"] == "auth"
        assert attrs["kind"] == "how-to"
        assert len(attrs["source_hash"]) == 64

    def test_freshly_generated_doc_is_current(self, help_dir: Path, project_root: Path) -> None:
        """check_staleness reports the doc as current right after generation."""
        _write_features_yaml(help_dir, self._MANIFEST)
        manifest = load_manifest(help_dir)

        generate_feature_templates(
            feature=manifest.features["auth"],
            help_dir=help_dir,
            project_root=project_root,
            depths=["how-to"],
        )

        report = check_staleness(manifest, help_dir, project_root, features=["auth"])
        auth_docs = [d for d in report.doc_entries if d.feature == "auth"]
        assert len(auth_docs) == 1
        assert auth_docs[0].is_stale is False
        assert auth_docs[0].missing is False
        assert auth_docs[0].stored_hash == auth_docs[0].current_hash

    def test_source_change_marks_doc_stale(self, help_dir: Path, project_root: Path) -> None:
        """Modifying a source file after generation flips the doc to stale."""
        _write_features_yaml(help_dir, self._MANIFEST)
        manifest = load_manifest(help_dir)

        generate_feature_templates(
            feature=manifest.features["auth"],
            help_dir=help_dir,
            project_root=project_root,
            depths=["how-to"],
        )

        (project_root / "src" / "auth" / "login.py").write_text(
            '"""Login handler — updated behaviour."""\n',
            encoding="utf-8",
        )

        report = check_staleness(manifest, help_dir, project_root, features=["auth"])
        auth_docs = [d for d in report.doc_entries if d.feature == "auth"]
        assert len(auth_docs) == 1
        assert auth_docs[0].is_stale is True
        assert auth_docs[0].missing is False
        assert auth_docs[0].stored_hash != auth_docs[0].current_hash

    def test_missing_doc_is_stale(self, help_dir: Path, project_root: Path) -> None:
        """A doc_path declared in the manifest but not on disk is stale."""
        _write_features_yaml(help_dir, self._MANIFEST)
        manifest = load_manifest(help_dir)

        report = check_staleness(manifest, help_dir, project_root, features=["auth"])
        auth_docs = [d for d in report.doc_entries if d.feature == "auth"]
        assert len(auth_docs) == 1
        assert auth_docs[0].missing is True
        assert auth_docs[0].is_stale is True


class TestMultiDocPathWarning:
    """Generator warns when doc_paths has more than one entry.

    Guards the scope note at ``_project_doc_output_path``:
    multi-path generation is a planned follow-on, so users should
    see a visible signal when additional paths are being ignored.
    """

    _MANIFEST = (
        "version: 1\n"
        "features:\n"
        "  auth:\n"
        "    description: Authentication and authorization\n"
        "    files: [src/auth/**]\n"
        "    doc_paths:\n"
        "      - docs/how-to/auth.md\n"
        "      - docs/how-to/auth-advanced.md\n"
    )

    def test_multi_doc_paths_logs_warning(
        self,
        help_dir: Path,
        project_root: Path,
        caplog,
    ) -> None:
        """Generation warns and names the skipped paths when doc_paths > 1."""
        _write_features_yaml(help_dir, self._MANIFEST)
        manifest = load_manifest(help_dir)

        with caplog.at_level(logging.WARNING, logger="attune_author.generator"):
            generate_feature_templates(
                feature=manifest.features["auth"],
                help_dir=help_dir,
                project_root=project_root,
                depths=["how-to"],
            )

        assert any(
            "doc_paths" in r.message and "auth-advanced.md" in r.message for r in caplog.records
        ), f"expected multi-doc_paths warning; got: {[r.message for r in caplog.records]}"

    def test_single_doc_path_is_silent(
        self,
        help_dir: Path,
        project_root: Path,
        caplog,
    ) -> None:
        """Single doc_path does not trigger the multi-path warning."""
        single = (
            "version: 1\n"
            "features:\n"
            "  auth:\n"
            "    description: Auth\n"
            "    files: [src/auth/**]\n"
            "    doc_path: docs/how-to/auth.md\n"
        )
        _write_features_yaml(help_dir, single)
        manifest = load_manifest(help_dir)

        with caplog.at_level(logging.WARNING, logger="attune_author.generator"):
            generate_feature_templates(
                feature=manifest.features["auth"],
                help_dir=help_dir,
                project_root=project_root,
                depths=["how-to"],
            )

        multi_warnings = [r for r in caplog.records if "doc_paths" in r.message]
        assert multi_warnings == []
