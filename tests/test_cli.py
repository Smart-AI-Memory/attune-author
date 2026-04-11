"""Tests for attune_author.cli."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from attune_author.cli import main


class TestCLI:
    """Tests for the CLI entry point."""

    def test_no_args_shows_welcome(self, tmp_path: Path, capsys, monkeypatch) -> None:
        """Bare `attune-author` in a fresh directory shows the
        'not set up yet' welcome pointing at `init`."""
        monkeypatch.chdir(tmp_path)
        result = main([])
        assert result == 0

        captured = capsys.readouterr()
        assert "attune-author" in captured.out
        assert "isn't set up yet" in captured.out
        assert "attune-author init" in captured.out

    def test_welcome_with_manifest(self, tmp_path: Path, capsys, monkeypatch) -> None:
        """Bare `attune-author` in an initialized project lists
        feature names and suggests `status` / `generate`."""
        help_dir = tmp_path / ".help"
        help_dir.mkdir()
        (help_dir / "features.yaml").write_text(
            "version: 1\n"
            "features:\n"
            "  auth:\n"
            "    description: Authentication\n"
            "  api:\n"
            "    description: REST API\n",
            encoding="utf-8",
        )
        monkeypatch.chdir(tmp_path)
        result = main([])
        assert result == 0

        captured = capsys.readouterr()
        assert "Found 2 features" in captured.out
        assert "auth" in captured.out
        assert "api" in captured.out
        assert "generate <feature>" in captured.out
        assert "attune-author status" in captured.out

    def test_welcome_with_broken_manifest(
        self,
        tmp_path: Path,
        capsys,
        monkeypatch,
    ) -> None:
        """A malformed features.yaml must fall through to the
        'not set up yet' screen without raising."""
        help_dir = tmp_path / ".help"
        help_dir.mkdir()
        # Invalid YAML content
        (help_dir / "features.yaml").write_text("not: [valid: yaml", encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        result = main([])
        assert result == 0

        captured = capsys.readouterr()
        assert "isn't set up yet" in captured.out

    def test_welcome_truncates_long_feature_list(
        self,
        tmp_path: Path,
        capsys,
        monkeypatch,
    ) -> None:
        """When a project has more than 8 features, the welcome
        screen truncates with an ellipsis so a huge project
        doesn't spam the terminal."""
        help_dir = tmp_path / ".help"
        help_dir.mkdir()
        feature_block = "\n".join(
            f"  feat{i:02d}:\n    description: Feature {i}" for i in range(12)
        )
        (help_dir / "features.yaml").write_text(
            f"version: 1\nfeatures:\n{feature_block}\n",
            encoding="utf-8",
        )
        monkeypatch.chdir(tmp_path)
        result = main([])
        assert result == 0

        captured = capsys.readouterr()
        assert "Found 12 features" in captured.out
        # First 8 sorted feature names must appear
        for i in range(8):
            assert f"feat{i:02d}" in captured.out
        # Ninth onwards must be truncated
        assert "feat11" not in captured.out
        assert "…" in captured.out

    def test_version_flag(self, capsys) -> None:
        """Test --version flag."""
        import pytest

        with pytest.raises(SystemExit, match="0"):
            main(["--version"])

    def test_init_creates_manifest(self, tmp_path: Path, capsys) -> None:
        """Test init command creates features.yaml."""
        # Create minimal source structure
        src = tmp_path / "src" / "myapp"
        src.mkdir(parents=True)
        (src / "__init__.py").write_text('"""App."""\n')
        mod = src / "module"
        mod.mkdir()
        (mod / "__init__.py").write_text('"""Module."""\n')
        (mod / "core.py").write_text("x = 1\n")
        (mod / "utils.py").write_text("y = 2\n")
        (mod / "helpers.py").write_text("z = 3\n")

        result = main(["init", "--project-root", str(tmp_path)])

        assert result == 0
        assert (tmp_path / ".help" / "features.yaml").exists()

    def test_init_skips_if_exists(self, project_root: Path, help_dir: Path, capsys) -> None:
        """Test init command skips if already initialized."""
        result = main(["init", "--project-root", str(project_root)])

        assert result == 0
        captured = capsys.readouterr()
        assert "Already initialized" in captured.out

    def test_status_shows_report(self, help_dir: Path, project_root: Path, capsys) -> None:
        """Test status command shows staleness report."""
        result = main(
            [
                "status",
                "--help-dir",
                str(help_dir),
                "--project-root",
                str(project_root),
            ]
        )

        assert result == 0
        captured = capsys.readouterr()
        assert "Help Status" in captured.out

    def test_generate_feature(self, help_dir: Path, project_root: Path, capsys) -> None:
        """Test generate command creates templates."""
        with patch.dict("os.environ", {}, clear=False):
            result = main(
                [
                    "generate",
                    "auth",
                    "--help-dir",
                    str(help_dir),
                    "--project-root",
                    str(project_root),
                ]
            )

        assert result == 0
        captured = capsys.readouterr()
        assert "Generated" in captured.out

    def test_generate_unknown_feature(self, help_dir: Path, project_root: Path, capsys) -> None:
        """Test generate command with unknown feature."""
        result = main(
            [
                "generate",
                "nonexistent",
                "--help-dir",
                str(help_dir),
                "--project-root",
                str(project_root),
            ]
        )

        assert result == 1
        captured = capsys.readouterr()
        assert "not found" in captured.out

    def test_regenerate_dry_run(self, help_dir: Path, project_root: Path, capsys) -> None:
        """Test regenerate --dry-run."""
        result = main(
            [
                "regenerate",
                "--help-dir",
                str(help_dir),
                "--project-root",
                str(project_root),
                "--dry-run",
            ]
        )

        assert result == 0
        captured = capsys.readouterr()
        assert "Stale features:" in captured.out
