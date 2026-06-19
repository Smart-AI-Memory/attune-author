"""Tests for the ``cli_command`` field on the manifest Feature model."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

from attune_author.manifest import Feature, load_manifest, save_manifest


def test_feature_default_cli_command_is_none() -> None:
    feature = Feature(name="demo", description="x")
    assert feature.cli_command is None


def test_feature_accepts_cli_command_in_constructor() -> None:
    feature = Feature(name="demo", description="x", cli_command="ops")
    assert feature.cli_command == "ops"


def test_load_manifest_parses_cli_command(tmp_path: Path) -> None:
    (tmp_path / "features.yaml").write_text(
        dedent(
            """
            version: 1
            features:
              ops-dashboard:
                description: Ops dashboard
                cli_command: ops
              other:
                description: No CLI
            """
        ),
        encoding="utf-8",
    )

    manifest = load_manifest(tmp_path)
    assert manifest.features["ops-dashboard"].cli_command == "ops"
    assert manifest.features["other"].cli_command is None


def test_save_manifest_round_trips_cli_command(tmp_path: Path) -> None:
    from attune_author.manifest import FeatureManifest

    manifest = FeatureManifest(
        version=1,
        features={
            "ops-dashboard": Feature(
                name="ops-dashboard",
                description="Ops dashboard",
                cli_command="ops",
            ),
            "plain": Feature(name="plain", description="No CLI"),
        },
    )

    save_manifest(manifest, tmp_path)
    reloaded = load_manifest(tmp_path)

    assert reloaded.features["ops-dashboard"].cli_command == "ops"
    assert reloaded.features["plain"].cli_command is None


def test_save_manifest_omits_cli_command_when_none(tmp_path: Path) -> None:
    """Empty fields stay out of saved YAML so legacy manifests round-trip clean."""
    from attune_author.manifest import FeatureManifest

    manifest = FeatureManifest(
        version=1,
        features={
            "plain": Feature(name="plain", description="x"),
        },
    )
    out = save_manifest(manifest, tmp_path)
    text = out.read_text(encoding="utf-8")
    assert "cli_command" not in text
