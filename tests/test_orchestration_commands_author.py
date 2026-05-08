"""Tests for the moved ``author.*`` orchestration commands.

Phase D2. Each command is exercised by patching the underlying
authoring helpers so the tests stay fast and don't touch real LLM
or filesystem state. The end-to-end ``run_command`` path is also
covered so the registration side-effect is verifiable.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from attune_author.orchestration import (
    JobContext,
    ValidationError,
    list_commands,
    run_command,
)


@pytest.fixture(autouse=True)
def _import_author_commands():
    """Ensure registration happens fresh per test."""
    sys.modules.pop("attune_author.orchestration.commands.author", None)
    import attune_author.orchestration.commands.author  # noqa: F401


def _ctx() -> JobContext:
    return JobContext(job_id="t-1", log=lambda _line: None)


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def test_all_six_author_commands_registered() -> None:
    names = {s.name for s in list_commands()}
    expected = {
        "author.init",
        "author.status",
        "author.maintain",
        "author.lookup",
        "author.regen",
        "author.setup",
    }
    assert expected.issubset(names), names


# ---------------------------------------------------------------------------
# author.init
# ---------------------------------------------------------------------------


def test_init_skips_when_manifest_exists(tmp_path: Path) -> None:
    help_dir = tmp_path / ".help"
    help_dir.mkdir()
    (help_dir / "features.yaml").write_text("version: 1\nfeatures: {}\n")

    async def go():
        return await run_command("author.init", {"project_root": str(tmp_path)}, _ctx())

    result = asyncio.run(go())
    assert result.output["already_initialized"] is True


def test_init_reports_no_proposals(tmp_path: Path) -> None:
    with patch("attune_author.bootstrap.scan_project", return_value=[]):

        async def go():
            return await run_command("author.init", {"project_root": str(tmp_path)}, _ctx())

        result = asyncio.run(go())
    assert result.output["discovered"] == 0


# ---------------------------------------------------------------------------
# author.status
# ---------------------------------------------------------------------------


def test_status_returns_stale_and_fresh_counts(tmp_path: Path) -> None:
    help_dir = tmp_path / ".help"
    help_dir.mkdir()
    (help_dir / "features.yaml").write_text("version: 1\nfeatures: {}\n")

    feat = SimpleNamespace(name="auth")
    manifest = SimpleNamespace(features={"auth": feat})
    report = SimpleNamespace(stale_count=1, current_count=4)

    with (
        patch("attune_author.manifest.load_manifest", return_value=manifest),
        patch("attune_author.staleness.check_staleness", return_value=report),
        patch("attune_author.maintenance.format_status_report", return_value="report-text"),
    ):

        async def go():
            return await run_command("author.status", {"project_path": str(tmp_path)}, _ctx())

        result = asyncio.run(go())

    assert result.output["stale"] == 1
    assert result.output["fresh"] == 4
    assert result.output["total"] == 5
    assert result.output["report"] == "report-text"


def test_status_requires_explicit_paths() -> None:
    """The orchestration helper has no workspace fallback — empty args fail loudly."""

    async def go():
        await run_command("author.status", {}, _ctx())

    with pytest.raises(ValidationError):
        asyncio.run(go())


# ---------------------------------------------------------------------------
# author.maintain
# ---------------------------------------------------------------------------


def test_maintain_dry_run_skips_regeneration(tmp_path: Path) -> None:
    help_dir = tmp_path / ".help"
    help_dir.mkdir()
    (help_dir / "features.yaml").write_text("version: 1\nfeatures: {}\n")

    manifest = SimpleNamespace(features={})
    report = SimpleNamespace(stale_count=2, current_count=3, help_entries=[])

    with (
        patch("attune_author.manifest.load_manifest", return_value=manifest),
        patch("attune_author.staleness.check_staleness", return_value=report),
    ):

        async def go():
            return await run_command(
                "author.maintain",
                {"project_path": str(tmp_path), "dry_run": True},
                _ctx(),
            )

        result = asyncio.run(go())

    assert result.output["dry_run"] is True
    assert result.output["regenerated"] == []
    assert result.output["stale_count"] == 2


def test_maintain_returns_project_root_for_host_invalidation(tmp_path: Path) -> None:
    help_dir = tmp_path / ".help"
    help_dir.mkdir()
    (help_dir / "features.yaml").write_text("version: 1\nfeatures: {}\n")

    manifest = SimpleNamespace(features={})
    report = SimpleNamespace(stale_count=0, current_count=0, help_entries=[])

    with (
        patch("attune_author.manifest.load_manifest", return_value=manifest),
        patch("attune_author.staleness.check_staleness", return_value=report),
    ):

        async def go():
            return await run_command("author.maintain", {"project_path": str(tmp_path)}, _ctx())

        result = asyncio.run(go())

    assert result.output["project_root"] == str(tmp_path.resolve())


# ---------------------------------------------------------------------------
# author.lookup
# ---------------------------------------------------------------------------


def test_lookup_loads_template(tmp_path: Path) -> None:
    help_dir = tmp_path / ".help"
    (help_dir / "templates" / "auth").mkdir(parents=True)
    (help_dir / "templates" / "auth" / "concept.md").write_text("# Auth\nbody\n")

    manifest = SimpleNamespace(features={"auth": SimpleNamespace(name="auth")})

    with (
        patch("attune_author.manifest.load_manifest", return_value=manifest),
        patch("attune_author.manifest.resolve_topic", return_value="auth"),
        patch("attune_author.manifest.is_safe_feature_name", return_value=True),
    ):

        async def go():
            return await run_command(
                "author.lookup",
                {"query": "auth", "depth": "concept", "help_dir": str(help_dir)},
                _ctx(),
            )

        result = asyncio.run(go())

    assert result.output["feature"] == "auth"
    assert result.output["depth"] == "concept"
    assert "Auth" in result.output["content"]


def test_lookup_unknown_topic_raises_validation_error(tmp_path: Path) -> None:
    manifest = SimpleNamespace(features={"auth": SimpleNamespace(name="auth")})

    with (
        patch("attune_author.manifest.load_manifest", return_value=manifest),
        patch("attune_author.manifest.resolve_topic", return_value=None),
    ):

        async def go():
            await run_command(
                "author.lookup",
                {"query": "nope", "help_dir": str(tmp_path)},
                _ctx(),
            )

        with pytest.raises(ValidationError):
            asyncio.run(go())


# ---------------------------------------------------------------------------
# author.regen
# ---------------------------------------------------------------------------


def test_regen_unknown_feature_raises_validation_error(tmp_path: Path) -> None:
    help_dir = tmp_path / ".help"
    help_dir.mkdir()
    (help_dir / "features.yaml").write_text("version: 1\nfeatures: {}\n")

    manifest = SimpleNamespace(features={"auth": SimpleNamespace(name="auth")})

    with patch("attune_author.manifest.load_manifest", return_value=manifest):

        async def go():
            await run_command(
                "author.regen",
                {"project_path": str(tmp_path), "feature": "ghost"},
                _ctx(),
            )

        with pytest.raises(ValidationError):
            asyncio.run(go())


def test_regen_returns_project_root_for_host_invalidation(tmp_path: Path) -> None:
    help_dir = tmp_path / ".help"
    help_dir.mkdir()
    (help_dir / "features.yaml").write_text("version: 1\nfeatures: {}\n")

    manifest = SimpleNamespace(features={})

    with patch("attune_author.manifest.load_manifest", return_value=manifest):

        async def go():
            return await run_command("author.regen", {"project_path": str(tmp_path)}, _ctx())

        result = asyncio.run(go())

    assert result.output["project_root"] == str(tmp_path.resolve())
    assert result.output["generated"] == []


# ---------------------------------------------------------------------------
# author.setup
# ---------------------------------------------------------------------------


def test_setup_skips_init_when_manifest_present(tmp_path: Path) -> None:
    help_dir = tmp_path / ".help"
    help_dir.mkdir()
    (help_dir / "features.yaml").write_text("version: 1\nfeatures: {}\n")

    manifest = SimpleNamespace(features={})

    with patch("attune_author.manifest.load_manifest", return_value=manifest):

        async def go():
            return await run_command("author.setup", {"project_path": str(tmp_path)}, _ctx())

        result = asyncio.run(go())

    assert result.output["features_total"] == 0
    assert result.output["project_root"] == str(tmp_path.resolve())


def test_setup_init_no_proposals_returns_early(tmp_path: Path) -> None:
    """Empty project: scan finds nothing, helper returns early without touching disk."""
    with patch("attune_author.bootstrap.scan_project", return_value=[]):

        async def go():
            return await run_command("author.setup", {"project_path": str(tmp_path)}, _ctx())

        result = asyncio.run(go())

    assert result.output["discovered"] == 0


# ---------------------------------------------------------------------------
# Helper sanity
# ---------------------------------------------------------------------------


def test_resolve_project_paths_requires_absolute() -> None:
    from attune_author.orchestration._helpers import resolve_project_paths

    with pytest.raises(ValidationError):
        resolve_project_paths({"project_path": "relative/path"})


def test_resolve_project_paths_explicit_pair(tmp_path: Path) -> None:
    from attune_author.orchestration._helpers import resolve_project_paths

    help_dir = tmp_path / ".help"
    help_dir.mkdir()
    (help_dir / "features.yaml").write_text("v: 1\n")

    root, hd = resolve_project_paths({"project_root": str(tmp_path), "help_dir": str(help_dir)})
    assert root == tmp_path.resolve()
    assert hd == help_dir.resolve()


def test_resolve_project_paths_no_args_raises() -> None:
    from attune_author.orchestration._helpers import resolve_project_paths

    with pytest.raises(ValidationError):
        resolve_project_paths({})
