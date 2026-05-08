"""Shared utilities for orchestration command executors.

The path-resolution helpers here moved out of attune-gui's
``commands.py`` along with the ``author.*`` executors in Phase D2.
The attune-author copy intentionally drops the
``attune_gui.workspace.get_workspace()`` fallback — that fallback
belongs in the host (gui), not in the orchestration runtime. Hosts
that want workspace-driven defaults preprocess ``args`` before
calling :func:`attune_author.orchestration.run_command`.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from attune_author.orchestration.exceptions import ValidationError

logger = logging.getLogger(__name__)


def _require_absolute(field: str, raw: str) -> None:
    """Reject relative paths so callers see a clear error.

    Without this, ``Path('foo').resolve()`` joins ``foo`` to the
    runtime cwd and produces confusing paths in downstream errors.
    """

    if raw.startswith("/") or raw.startswith("~"):
        return
    raise ValidationError(
        f"{field} must be an absolute path (e.g. /Users/you/project) "
        f"or start with ~ (e.g. ~/project), got: {raw!r}"
    )


def _autopromote_to_manifest_dir(help_dir: Path) -> Path:
    """Promote ``help_dir`` to its parent when ``features.yaml`` lives one
    level up (the path picker often lands on ``.help/templates`` instead
    of ``.help``)."""

    if (help_dir / "features.yaml").exists():
        return help_dir
    parent = help_dir.parent
    if parent != help_dir and (parent / "features.yaml").exists():
        logger.info(
            "Auto-promoted help_dir from %s to %s (features.yaml lives in parent)",
            help_dir,
            parent,
        )
        return parent
    return help_dir


def resolve_project_paths(args: dict[str, Any]) -> tuple[Path, Path]:
    """Resolve ``(project_root, help_dir)`` from ``args``.

    Priority:

    1. ``project_path`` — convenience key; ``help_dir`` becomes
       ``<root>/.help`` (with autopromote).
    2. ``project_root`` / ``help_dir`` — explicit pair, both required
       and absolute.

    Raises :class:`ValidationError` if neither is supplied. Hosts that
    want a workspace-driven fallback should preprocess ``args`` before
    calling — orchestration commands are pure given their inputs.
    """

    project_path_raw = str(args.get("project_path", "")).strip()
    if project_path_raw:
        _require_absolute("project_path", project_path_raw)
        project_root = Path(project_path_raw).expanduser().resolve()
        return project_root, _autopromote_to_manifest_dir(project_root / ".help")

    project_root_raw = str(args.get("project_root", "")).strip()
    help_dir_raw = str(args.get("help_dir", "")).strip()

    if not project_root_raw or not help_dir_raw:
        raise ValidationError(
            "project_path (or both project_root and help_dir) must be supplied "
            "as absolute paths."
        )

    _require_absolute("project_root", project_root_raw)
    _require_absolute("help_dir", help_dir_raw)
    return (
        Path(project_root_raw).expanduser().resolve(),
        _autopromote_to_manifest_dir(Path(help_dir_raw).expanduser().resolve()),
    )
