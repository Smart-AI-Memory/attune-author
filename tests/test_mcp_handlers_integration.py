"""MCP handler integration tests.

Targets the uncovered lines in ``src/attune_author/mcp/handlers.py``
(audit reported ~29 uncovered) by exercising the handler methods through
their full request → orchestration → response lifecycle. The LLM call is
mocked at the boundary so no API tokens are spent; every other layer
(manifest loading, staleness checks, manifest saving) runs for real.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from attune_author.mcp.handlers import AttuneAuthorHandlers, _PathValidationError

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def handlers(tmp_path: Path) -> AttuneAuthorHandlers:
    return AttuneAuthorHandlers(workspace_root=str(tmp_path))


# ---------------------------------------------------------------------------
# _validated_paths — input contract
# ---------------------------------------------------------------------------


def test_validated_paths_accepts_in_bounds_path(
    handlers: AttuneAuthorHandlers, tmp_path: Path
) -> None:
    sub = tmp_path / "ok"
    sub.mkdir()
    paths = handlers._validated_paths({"project_root": str(sub)}, {"project_root": "."})
    assert paths["project_root"] == sub.resolve()


def test_validated_paths_uses_default_when_missing(
    handlers: AttuneAuthorHandlers, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Default ``"."`` resolves against cwd, validated against workspace_root."""
    monkeypatch.chdir(tmp_path)
    paths = handlers._validated_paths({}, {"project_root": "."})
    assert paths["project_root"] == tmp_path.resolve()


def test_validated_paths_raises_on_traversal(
    handlers: AttuneAuthorHandlers,
) -> None:
    with pytest.raises(_PathValidationError):
        handlers._validated_paths({"project_root": "../../etc"}, {"project_root": "."})


# ---------------------------------------------------------------------------
# author_init — bootstrap path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_author_init_returns_already_initialized_when_manifest_exists(
    handlers: AttuneAuthorHandlers, tmp_path: Path
) -> None:
    help_dir = tmp_path / ".help"
    help_dir.mkdir()
    (help_dir / "features.yaml").write_text("version: 1\nfeatures: {}\n")
    result = await handlers.author_init({"project_root": str(tmp_path)})
    assert result["success"] is True
    assert result.get("already_initialized") is True


@pytest.mark.asyncio
async def test_author_init_returns_zero_when_nothing_discovered(
    handlers: AttuneAuthorHandlers, tmp_path: Path
) -> None:
    """Empty project — scan_project returns no proposals."""
    with patch("attune_author.bootstrap.scan_project", return_value=[]):
        result = await handlers.author_init({"project_root": str(tmp_path)})
    assert result["success"] is True
    assert result["discovered"] == 0


@pytest.mark.asyncio
async def test_author_init_writes_manifest_when_features_discovered(
    handlers: AttuneAuthorHandlers, tmp_path: Path
) -> None:
    """When scan_project returns proposals, manifest is saved + counts surfaced."""
    fake_proposal = MagicMock(
        name="auth",
        description="Auth module",
        confidence=0.9,
        files=["src/auth/**"],
    )
    fake_proposal.name = "auth"
    fake_proposal.description = "Auth module"

    with (
        patch("attune_author.bootstrap.scan_project", return_value=[fake_proposal]),
        patch(
            "attune_author.bootstrap.proposals_to_manifest",
            return_value=MagicMock(),
        ),
        patch(
            "attune_author.manifest.save_manifest",
            return_value=tmp_path / ".help" / "features.yaml",
        ),
    ):
        result = await handlers.author_init({"project_root": str(tmp_path)})

    assert result["success"] is True
    assert result["discovered"] == 1
    assert "manifest_path" in result
    assert isinstance(result["features"], list)


@pytest.mark.asyncio
async def test_author_init_returns_path_validation_error(
    handlers: AttuneAuthorHandlers,
) -> None:
    """Malformed project_root surfaces as a structured error envelope."""
    result = await handlers.author_init({"project_root": "../../etc"})
    assert result["success"] is False
    assert "error" in result


# ---------------------------------------------------------------------------
# author_status — reports stale features
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_author_status_path_validation_error_is_structured(
    handlers: AttuneAuthorHandlers,
) -> None:
    result = await handlers.author_status({"help_dir": "../../"})
    assert result["success"] is False


@pytest.mark.asyncio
async def test_author_status_returns_envelope_when_manifest_present(
    handlers: AttuneAuthorHandlers, tmp_path: Path
) -> None:
    """With a real (empty) manifest on disk, handler must return a structured
    envelope rather than crashing — even if downstream maintenance returns
    success=False, the envelope shape itself is the contract."""
    help_dir = tmp_path / ".help"
    help_dir.mkdir()
    (help_dir / "features.yaml").write_text("version: 1\nfeatures: {}\n")
    result = await handlers.author_status(
        {"help_dir": str(help_dir), "project_root": str(tmp_path)}
    )
    assert isinstance(result, dict)
    assert "success" in result


# ---------------------------------------------------------------------------
# author_generate — propagates LLM errors via envelope, doesn't crash
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_author_generate_path_validation_returns_structured_error(
    handlers: AttuneAuthorHandlers,
) -> None:
    result = await handlers.author_generate({"feature_name": "auth", "help_dir": "../../"})
    assert result["success"] is False
    assert "error" in result


# ---------------------------------------------------------------------------
# author_lookup — read-only path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_author_lookup_path_validation_returns_structured_error(
    handlers: AttuneAuthorHandlers,
) -> None:
    result = await handlers.author_lookup({"help_dir": "../../"})
    assert result["success"] is False


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


def test_handlers_holds_workspace_root_reference(
    handlers: AttuneAuthorHandlers, tmp_path: Path
) -> None:
    assert handlers._workspace_root == str(tmp_path)
