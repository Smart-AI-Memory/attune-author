"""Tests for the CLI ``--help`` ground-truth extractor."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from attune_author.ground_truth import cli_help


@pytest.fixture(autouse=True)
def _clear_cli_help_cache() -> None:
    """Each test gets a fresh per-process cache."""
    cli_help.clear_cache()
    yield
    cli_help.clear_cache()


def _completed(returncode: int, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(
        args=["fake"],
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


def test_help_capture_on_success(tmp_path: Path) -> None:
    with patch.object(cli_help.subprocess, "run") as mock_run:
        mock_run.return_value = _completed(0, "Usage: attune ops [OPTIONS]\n")
        result = cli_help.extract_cli_help("attune", "ops", project_root=tmp_path)

    assert "Usage: attune ops" in result
    mock_run.assert_called_once()


def test_help_returns_empty_on_nonzero_exit(tmp_path: Path) -> None:
    with patch.object(cli_help.subprocess, "run") as mock_run:
        mock_run.return_value = _completed(2, "", "no such command\n")
        result = cli_help.extract_cli_help("attune", "nonexistent", project_root=tmp_path)

    assert result == ""


def test_help_returns_empty_on_timeout(tmp_path: Path) -> None:
    with patch.object(cli_help.subprocess, "run") as mock_run:
        mock_run.side_effect = subprocess.TimeoutExpired(cmd=["attune"], timeout=10)
        result = cli_help.extract_cli_help("attune", "ops", project_root=tmp_path)

    assert result == ""


def test_help_returns_empty_on_missing_executable(tmp_path: Path) -> None:
    with patch.object(cli_help.subprocess, "run") as mock_run:
        mock_run.side_effect = FileNotFoundError("attune: not found")
        result = cli_help.extract_cli_help("attune", "ops", project_root=tmp_path)

    assert result == ""


def test_help_caches_repeated_calls(tmp_path: Path) -> None:
    """Same (executable, subcommand, cwd) tuple should hit the cache."""
    with patch.object(cli_help.subprocess, "run") as mock_run:
        mock_run.return_value = _completed(0, "help output\n")
        cli_help.extract_cli_help("attune", "ops", project_root=tmp_path)
        cli_help.extract_cli_help("attune", "ops", project_root=tmp_path)

    assert mock_run.call_count == 1


def test_help_empty_args_returns_empty(tmp_path: Path) -> None:
    assert cli_help.extract_cli_help("", "ops", project_root=tmp_path) == ""
    assert cli_help.extract_cli_help("attune", "", project_root=tmp_path) == ""
