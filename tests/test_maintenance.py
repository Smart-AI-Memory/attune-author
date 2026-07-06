"""Tests for attune_author.maintenance."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from attune_author.auth import AUTH_MODE_ENV
from attune_author.maintenance import (
    format_status_report,
    get_changed_files,
    run_hook,
    run_maintenance,
)
from attune_author.polish import PolishError
from attune_author.staleness import FeatureStaleness, StalenessReport


class TestRunMaintenance:
    """Tests for run_maintenance()."""

    def test_dry_run_reports_staleness(self, help_dir: Path, project_root: Path) -> None:
        """Test dry run reports stale features without regenerating."""
        result = run_maintenance(
            help_dir=help_dir,
            project_root=project_root,
            dry_run=True,
        )

        assert result.stale_count > 0
        assert result.regenerated_count == 0

    def test_regenerates_stale_features(self, help_dir: Path, project_root: Path) -> None:
        """Test that stale features get regenerated."""
        with patch.dict("os.environ", {}, clear=False):
            result = run_maintenance(
                help_dir=help_dir,
                project_root=project_root,
            )

        assert result.regenerated_count > 0

    def test_filter_by_feature(self, help_dir: Path, project_root: Path) -> None:
        """Test regenerating specific features only."""
        with patch.dict("os.environ", {}, clear=False):
            result = run_maintenance(
                help_dir=help_dir,
                project_root=project_root,
                features=["auth"],
            )

        # Only auth should be processed
        if result.regenerated:
            assert all(r.feature == "auth" for r in result.regenerated)

    def test_polish_error_marks_failed_and_continues(
        self, help_dir: Path, project_root: Path
    ) -> None:
        """A strict-polish failure on one feature must not abort the loop."""
        with patch(
            "attune_author.maintenance.generate_feature_templates",
            side_effect=PolishError("nested SDK teardown"),
        ):
            result = run_maintenance(help_dir=help_dir, project_root=project_root)

        assert result.regenerated_count == 0
        # Both stale fixture features (auth, cli) were attempted —
        # the first PolishError did not short-circuit the second.
        assert result.failed == ["auth", "cli"]

    def test_no_op_when_all_current(self, help_dir: Path, project_root: Path) -> None:
        """Test that nothing is regenerated when all are current."""
        # Generate templates first
        with patch.dict("os.environ", {}, clear=False):
            run_maintenance(help_dir=help_dir, project_root=project_root)

        # Now run again — everything should be current
        with patch.dict("os.environ", {}, clear=False):
            result = run_maintenance(help_dir=help_dir, project_root=project_root)

        assert result.stale_count == 0
        assert result.regenerated_count == 0


class TestGetChangedFiles:
    """Tests for get_changed_files()."""

    def test_returns_files_from_git_diff(self, tmp_path: Path) -> None:
        """Test parsing git diff output."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "src/foo.py\nsrc/bar.py\n\n"
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            files = get_changed_files(tmp_path)

        assert files == ["src/foo.py", "src/bar.py"]

    def test_returns_empty_on_git_failure(self, tmp_path: Path) -> None:
        """Test empty list when git command fails."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "not a git repo"

        with patch("subprocess.run", return_value=mock_result):
            files = get_changed_files(tmp_path)

        assert files == []

    def test_returns_empty_on_timeout(self, tmp_path: Path) -> None:
        """Test empty list on subprocess timeout."""
        with patch(
            "subprocess.run",
            side_effect=subprocess.TimeoutExpired("git", 10),
        ):
            files = get_changed_files(tmp_path)

        assert files == []

    def test_returns_empty_on_os_error(self, tmp_path: Path) -> None:
        """Test empty list on OSError (git not installed)."""
        with patch("subprocess.run", side_effect=OSError("git not found")):
            files = get_changed_files(tmp_path)

        assert files == []


class TestRunHook:
    """Tests for run_hook()."""

    def test_returns_none_without_manifest(self, tmp_path: Path) -> None:
        """Test None when features.yaml doesn't exist."""
        help_dir = tmp_path / ".help"
        help_dir.mkdir()

        result = run_hook(help_dir=help_dir, project_root=tmp_path)
        assert result is None

    def test_returns_none_without_changed_files(self, help_dir: Path, project_root: Path) -> None:
        """Test None when no files were changed."""
        with patch(
            "attune_author.maintenance.get_changed_files",
            return_value=[],
        ):
            result = run_hook(help_dir=help_dir, project_root=project_root)

        assert result is None

    def test_returns_none_when_no_features_match(self, help_dir: Path, project_root: Path) -> None:
        """Test None when changed files don't match any feature."""
        with patch(
            "attune_author.maintenance.get_changed_files",
            return_value=["unrelated/path.txt"],
        ):
            result = run_hook(help_dir=help_dir, project_root=project_root)

        assert result is None

    def test_runs_maintenance_for_affected_features(
        self, help_dir: Path, project_root: Path
    ) -> None:
        """Test that affected features trigger maintenance."""
        with patch.dict("os.environ", {}, clear=False):
            with patch(
                "attune_author.maintenance.get_changed_files",
                return_value=["src/auth/login.py"],
            ):
                result = run_hook(help_dir=help_dir, project_root=project_root)

        assert result is not None
        assert result.regenerated_count > 0

    def test_nested_claude_code_without_key_skips_regen(
        self, help_dir: Path, project_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Nested session + no API key degrades to a dry-run report."""
        monkeypatch.setenv("CLAUDECODE", "1")
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        with patch(
            "attune_author.maintenance.get_changed_files",
            return_value=["src/auth/login.py"],
        ):
            with patch("attune_author.maintenance.generate_feature_templates") as gen:
                result = run_hook(help_dir=help_dir, project_root=project_root)

        assert result is not None
        assert result.stale_count > 0
        assert result.regenerated_count == 0
        gen.assert_not_called()

    def test_nested_claude_code_with_key_pins_api_route(
        self, help_dir: Path, project_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Nested session + API key regenerates via the API route.

        Auto mode tries the subscription route first, which in a
        claude-in-claude session spends the call and discards the
        result — so the hook must pin the mode to ``api`` and scrub
        the session's gateway URL before polish runs.
        """
        monkeypatch.setenv("CLAUDECODE", "1")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
        monkeypatch.setenv("ANTHROPIC_BASE_URL", "https://gateway.example")
        monkeypatch.delenv(AUTH_MODE_ENV, raising=False)

        with patch(
            "attune_author.maintenance.get_changed_files",
            return_value=["src/auth/login.py"],
        ):
            with patch(
                "attune_author.maintenance.generate_feature_templates",
                return_value=MagicMock(templates=[], feature="auth"),
            ):
                result = run_hook(help_dir=help_dir, project_root=project_root)

        assert result is not None
        assert result.regenerated_count > 0
        assert os.environ.get(AUTH_MODE_ENV) == "api"
        assert "ANTHROPIC_BASE_URL" not in os.environ

    def test_nested_claude_code_respects_forced_sub_mode(
        self, help_dir: Path, project_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """An explicit ATTUNE_AUTHOR_AUTH_MODE wins over the nested guard."""
        monkeypatch.setenv("CLAUDECODE", "1")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
        monkeypatch.setenv("ANTHROPIC_BASE_URL", "https://gateway.example")
        monkeypatch.setenv(AUTH_MODE_ENV, "sub")

        with patch(
            "attune_author.maintenance.get_changed_files",
            return_value=["src/auth/login.py"],
        ):
            with patch(
                "attune_author.maintenance.generate_feature_templates",
                return_value=MagicMock(templates=[], feature="auth"),
            ):
                run_hook(help_dir=help_dir, project_root=project_root)

        assert os.environ.get(AUTH_MODE_ENV) == "sub"
        assert os.environ.get("ANTHROPIC_BASE_URL") == "https://gateway.example"

    def test_loads_project_dotenv(
        self, help_dir: Path, project_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """run_hook picks up ANTHROPIC_API_KEY from the project .env.

        The hook enters via ``python -c``, bypassing ``cli.main()``
        and its ``load_dotenv()`` — run_hook must load the project
        .env itself or polish sees no credentials. The autouse
        fixture no-ops dotenv, so restore the real loader here.
        """
        import dotenv

        monkeypatch.setattr("dotenv.load_dotenv", dotenv.main.load_dotenv)
        monkeypatch.setenv("CLAUDECODE", "1")
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv(AUTH_MODE_ENV, raising=False)
        (project_root / ".env").write_text(
            "ANTHROPIC_API_KEY=sk-ant-from-dotenv\n",  # pragma: allowlist secret
            encoding="utf-8",
        )

        with patch(
            "attune_author.maintenance.get_changed_files",
            return_value=["src/auth/login.py"],
        ):
            with patch(
                "attune_author.maintenance.generate_feature_templates",
                return_value=MagicMock(templates=[], feature="auth"),
            ):
                result = run_hook(help_dir=help_dir, project_root=project_root)

        assert os.environ.get("ANTHROPIC_API_KEY") == "sk-ant-from-dotenv"
        # Key found → regen proceeded on the pinned API route rather
        # than degrading to the keyless dry-run report.
        assert result is not None
        assert result.regenerated_count > 0
        assert os.environ.get(AUTH_MODE_ENV) == "api"

    def test_nested_keyless_all_current_skips_warning(
        self, help_dir: Path, project_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Keyless nested path with nothing stale reports quietly."""
        # Bring everything current first (lenient polish, no LLM).
        run_maintenance(help_dir=help_dir, project_root=project_root)

        monkeypatch.setenv("CLAUDECODE", "1")
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        with patch(
            "attune_author.maintenance.get_changed_files",
            return_value=["src/auth/login.py"],
        ):
            result = run_hook(help_dir=help_dir, project_root=project_root)

        assert result is not None
        assert result.stale_count == 0
        assert result.regenerated_count == 0

    def test_survives_missing_dotenv_package(
        self, help_dir: Path, project_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """run_hook works when python-dotenv is not installed."""
        import sys

        monkeypatch.setitem(sys.modules, "dotenv", None)

        with patch(
            "attune_author.maintenance.get_changed_files",
            return_value=["src/auth/login.py"],
        ):
            with patch(
                "attune_author.maintenance.generate_feature_templates",
                return_value=MagicMock(templates=[], feature="auth"),
            ):
                result = run_hook(help_dir=help_dir, project_root=project_root)

        assert result is not None
        assert result.regenerated_count > 0

    def test_returns_none_on_invalid_manifest(self, tmp_path: Path) -> None:
        """Test None when manifest has invalid structure."""
        help_dir = tmp_path / ".help"
        help_dir.mkdir()
        # Valid YAML but invalid manifest structure (top-level list, not dict)
        (help_dir / "features.yaml").write_text("- not a mapping\n")

        with patch(
            "attune_author.maintenance.get_changed_files",
            return_value=["src/foo.py"],
        ):
            result = run_hook(help_dir=help_dir, project_root=tmp_path)

        assert result is None


class TestFormatStatusReport:
    """Tests for format_status_report()."""

    def test_formats_stale_report(self) -> None:
        """Test markdown formatting of a staleness report."""
        report = StalenessReport(
            help_entries=[
                FeatureStaleness(
                    feature="auth",
                    is_stale=True,
                    current_hash="abc",
                    stored_hash="xyz",
                    matched_files=["src/auth/login.py"],
                ),
                FeatureStaleness(
                    feature="cli",
                    is_stale=False,
                    current_hash="def",
                    stored_hash="def",
                ),
            ]
        )

        output = format_status_report(report)

        assert "Help Templates" in output
        assert "1** current" in output
        assert "1** stale" in output
        assert "auth" in output

    def test_all_current_report(self) -> None:
        """Test report with no stale features."""
        report = StalenessReport(
            help_entries=[
                FeatureStaleness(
                    feature="cli",
                    is_stale=False,
                    current_hash="def",
                    stored_hash="def",
                ),
            ]
        )

        output = format_status_report(report)
        assert "0** stale" in output
        assert "### Stale" not in output

    def test_all_stale_report(self) -> None:
        """Test report with all stale features."""
        report = StalenessReport(
            help_entries=[
                FeatureStaleness(
                    feature="auth",
                    is_stale=True,
                    current_hash="abc",
                    stored_hash=None,
                    matched_files=[],
                ),
            ]
        )

        output = format_status_report(report)
        assert "0** current" in output
        assert "### Stale" in output
