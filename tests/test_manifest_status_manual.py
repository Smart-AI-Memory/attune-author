"""Regression tests for manifest-level ``status: manual`` features.

Reproduces the attune-ai 2026-07-04 incident: the single-source
rollout removed ``files:`` from every feature and marked them
``status: manual``, but staleness had no manifest-status concept —
so every feature hashed to the empty digest, mismatched its stored
hash, and ``attune-author status`` reported the whole catalog
(27/27) stale with "0 source files" changed. Manual features must
be skipped by staleness, refused by generate (no LLM clobber of
projected content), and surfaced separately in the status report.
"""

from __future__ import annotations

from pathlib import Path

from attune_author.generator import generate_feature_templates
from attune_author.maintenance import format_status_report, run_maintenance
from attune_author.manifest import Feature, FeatureManifest, load_manifest, save_manifest
from attune_author.staleness import check_staleness


def _manual_help_dir(tmp_path: Path) -> Path:
    """A .help/ with one manual (files-less) and one auto feature."""
    help_dir = tmp_path / ".help"
    help_dir.mkdir()
    (help_dir / "features.yaml").write_text(
        "version: 1\n"
        "\n"
        "features:\n"
        "  projected:\n"
        "    description: Single-sourced feature, projector-owned\n"
        "    tags: [docs]\n"
        "    status: manual\n"
        "  auth:\n"
        "    description: Authentication\n"
        "    files:\n"
        "      - src/auth/**\n",
        encoding="utf-8",
    )
    # Projected feature has templates on disk with a stale-looking
    # stored hash — exactly the incident shape.
    tpl = help_dir / "templates" / "projected"
    tpl.mkdir(parents=True)
    (tpl / "concept.md").write_text(
        "---\n"
        "type: concept\n"
        "feature: projected\n"
        "source_hash: 544951b28662066a703ef7be552af08e83ef52a5186e5ad71ad2161\n"
        "status: generated\n"
        "---\n"
        "\n# Projected content — owned by the projector\n",
        encoding="utf-8",
    )
    (tmp_path / "src" / "auth").mkdir(parents=True)
    (tmp_path / "src" / "auth" / "core.py").write_text("def login():\n    pass\n", encoding="utf-8")
    return help_dir


class TestManifestStatusField:
    """Feature.status parsing and round-trip."""

    def test_default_is_auto(self) -> None:
        assert Feature(name="x", description="d").status == "auto"

    def test_load_parses_manual(self, tmp_path: Path) -> None:
        help_dir = _manual_help_dir(tmp_path)
        manifest = load_manifest(help_dir)
        assert manifest.features["projected"].status == "manual"
        assert manifest.features["auth"].status == "auto"

    def test_save_roundtrips_status(self, tmp_path: Path) -> None:
        manifest = FeatureManifest(
            version=1,
            features={
                "m": Feature(name="m", description="manual", status="manual"),
                "a": Feature(name="a", description="auto"),
            },
        )
        save_manifest(manifest, tmp_path / ".help")
        loaded = load_manifest(tmp_path / ".help")
        assert loaded.features["m"].status == "manual"
        assert loaded.features["a"].status == "auto"
        # "auto" is the default and must not be emitted.
        text = (tmp_path / ".help" / "features.yaml").read_text(encoding="utf-8")
        assert text.count("status:") == 1


class TestStalenessSkipsManual:
    """check_staleness must not empty-hash manual features."""

    def test_manual_feature_not_reported_stale(self, tmp_path: Path) -> None:
        help_dir = _manual_help_dir(tmp_path)
        manifest = load_manifest(help_dir)
        report = check_staleness(manifest, help_dir, tmp_path)
        assert report.manual_features == ["projected"]
        checked = {e.feature for e in report.help_entries}
        assert "projected" not in checked
        # The auto feature is still tracked normally.
        assert "auth" in checked
        assert report.stale_count == 1  # auth has no stored hash yet

    def test_feature_filter_still_skips_manual(self, tmp_path: Path) -> None:
        help_dir = _manual_help_dir(tmp_path)
        manifest = load_manifest(help_dir)
        report = check_staleness(manifest, help_dir, tmp_path, features=["projected"])
        assert report.help_entries == []
        assert report.manual_features == ["projected"]
        assert report.stale_count == 0


class TestGenerateRefusesManual:
    """generate must not clobber projector-owned content."""

    def test_generate_skips_manual_without_overwrite(self, tmp_path: Path) -> None:
        help_dir = _manual_help_dir(tmp_path)
        manifest = load_manifest(help_dir)
        concept = help_dir / "templates" / "projected" / "concept.md"
        before = concept.read_text(encoding="utf-8")
        result = generate_feature_templates(
            feature=manifest.features["projected"],
            help_dir=help_dir,
            project_root=tmp_path,
        )
        assert result.templates == []
        assert concept.read_text(encoding="utf-8") == before

    def test_run_maintenance_reports_skipped_manual(self, tmp_path: Path) -> None:
        help_dir = _manual_help_dir(tmp_path)
        result = run_maintenance(help_dir, tmp_path, dry_run=True)
        assert result.skipped_manual == ["projected"]


class TestStatusReportShowsManual:
    """format_status_report surfaces manual features separately."""

    def test_manual_count_and_section(self, tmp_path: Path) -> None:
        help_dir = _manual_help_dir(tmp_path)
        manifest = load_manifest(help_dir)
        report = check_staleness(manifest, help_dir, tmp_path)
        text = format_status_report(report, help_dir)
        assert "**1** manual (not tracked)" in text
        assert "projected" in text

    def test_no_manual_line_when_none(self, tmp_path: Path) -> None:
        help_dir = tmp_path / ".help"
        help_dir.mkdir()
        (help_dir / "features.yaml").write_text(
            "version: 1\nfeatures:\n  auth:\n    description: Auth\n"
            "    files:\n      - src/auth/**\n",
            encoding="utf-8",
        )
        manifest = load_manifest(help_dir)
        report = check_staleness(manifest, help_dir, tmp_path)
        text = format_status_report(report, help_dir)
        assert "manual (not tracked)" not in text
