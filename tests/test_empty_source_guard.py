"""Regression tests: refuse to overwrite templates from empty source.

2026-07-05 incident: a bulk regen run against a wrong project root
resolved every feature's globs to zero files, computed
``source_hash`` of the empty string
(e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855),
and rewrote 36 existing templates with drastically degraded content.
The generation pipeline must fail loudly (before any write) when
empty-resolved source would overwrite existing output. Scaffolding a
brand-new feature (nothing on disk yet) from empty source remains
allowed — see ``test_feature_glob_with_zero_matches`` in
``test_generator.py``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from attune_author import EMPTY_SOURCE_SHA256, EmptySourceError
from attune_author.generator import generate_feature_templates, prepare_polish_phase
from attune_author.manifest import Feature


@pytest.fixture
def feature() -> Feature:
    return Feature(
        name="auth",
        description="Authentication and authorization",
        files=["src/auth/**"],
        tags=["security"],
    )


GOOD_TEMPLATE = (
    "---\n"
    "type: concept\n"
    "name: auth-concept\n"
    "feature: auth\n"
    "depth: concept\n"
    "generated_at: 2026-06-23T00:00:00+00:00\n"
    "source_hash: 544951b28662066a703ef7be552af08e83ef52a5186e5ad71ad216119352938b\n"
    "status: generated\n"
    "---\n"
    "\n"
    "# Real polished content that must not be clobbered\n"
)


def _seed_existing_template(help_dir: Path) -> Path:
    """Put a healthy generated template on disk for feature 'auth'."""
    tdir = help_dir / "templates" / "auth"
    tdir.mkdir(parents=True)
    concept = tdir / "concept.md"
    concept.write_text(GOOD_TEMPLATE, encoding="utf-8")
    return concept


class TestEmptySourceOverwriteGuard:
    """Empty resolved source + existing output on disk → hard refuse."""

    def test_zero_matched_files_refuses_and_preserves_content(
        self, feature: Feature, help_dir: Path, tmp_path: Path
    ) -> None:
        concept = _seed_existing_template(help_dir)
        empty_root = tmp_path / "emptyroot"
        empty_root.mkdir()

        with pytest.raises(EmptySourceError, match="no files matched"):
            prepare_polish_phase(
                feature=feature,
                help_dir=help_dir,
                project_root=empty_root,
                overwrite=True,
            )

        # The guard fires before any write — existing content intact.
        assert concept.read_text(encoding="utf-8") == GOOD_TEMPLATE

    def test_all_empty_matched_files_refuses(
        self, feature: Feature, help_dir: Path, tmp_path: Path
    ) -> None:
        # Non-.py so the legacy byte-concatenation path is exercised;
        # zero bytes total → the empty-string SHA.
        _seed_existing_template(help_dir)
        root = tmp_path / "zerobyte"
        (root / "src" / "auth").mkdir(parents=True)
        (root / "src" / "auth" / "data.txt").write_bytes(b"")

        with pytest.raises(EmptySourceError, match="empty/unreadable"):
            prepare_polish_phase(
                feature=feature,
                help_dir=help_dir,
                project_root=root,
                overwrite=True,
            )

    def test_generate_feature_templates_propagates(
        self, feature: Feature, help_dir: Path, tmp_path: Path
    ) -> None:
        _seed_existing_template(help_dir)
        empty_root = tmp_path / "emptyroot"
        empty_root.mkdir()

        with pytest.raises(EmptySourceError):
            generate_feature_templates(
                feature=feature,
                help_dir=help_dir,
                project_root=empty_root,
                overwrite=True,
            )

    def test_scaffolding_new_feature_from_empty_source_allowed(
        self, feature: Feature, help_dir: Path, tmp_path: Path
    ) -> None:
        # No templates on disk → bootstrap scaffold stays permitted.
        empty_root = tmp_path / "emptyroot"
        empty_root.mkdir()

        prep = prepare_polish_phase(
            feature=feature,
            help_dir=help_dir,
            project_root=empty_root,
            overwrite=True,
        )
        assert prep.matched_files == []
        assert prep.pending

    def test_healthy_source_still_generates(
        self, feature: Feature, help_dir: Path, project_root: Path
    ) -> None:
        _seed_existing_template(help_dir)
        prep = prepare_polish_phase(
            feature=feature,
            help_dir=help_dir,
            project_root=project_root,
            overwrite=True,
        )
        assert prep.matched_files
        assert prep.source_hash != EMPTY_SOURCE_SHA256
        assert prep.pending


class TestEmptySourceCLI:
    """The CLI exits non-zero with a clear message — no traceback."""

    def test_generate_against_empty_root_exits_1(
        self, help_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        from attune_author.cli import main

        _seed_existing_template(help_dir)
        empty_root = tmp_path / "emptyroot"
        empty_root.mkdir()

        exit_code = main(
            [
                "generate",
                "auth",
                "--help-dir",
                str(help_dir),
                "--project-root",
                str(empty_root),
                "--overwrite",
            ]
        )
        assert exit_code == 1
        err = capsys.readouterr().err
        assert "Refusing to regenerate" in err
