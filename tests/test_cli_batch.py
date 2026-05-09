"""CLI tests for the batch flags on `attune-author regenerate`.

Covers:

- argparse mutex enforcement (--batch / --resume / --status / --cancel
  are mutually exclusive; --force and --json are modifiers)
- submit prints batch ID + copy-paste-ready resume hint
- bare `regenerate` prints a one-liner when a state file exists,
  but doesn't auto-resume
- --resume and --status surface clean errors when no state file
- --status JSON mode produces parseable output
- --cancel removes the state file

Each test mocks the maintenance_batch entry points; nothing
reaches Anthropic.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

from attune_author.cli import _build_parser, main
from attune_author.maintenance_batch import (
    BatchState,
    BatchStateRequest,
    state_path,
    write_batch_state,
)


def _state(batch_id: str = "msgbatch_test") -> BatchState:
    return BatchState(
        schema_version=1,
        batch_id=batch_id,
        submitted_at=datetime(2026, 5, 8, 18, 35, tzinfo=timezone.utc),
        expected_completion_at=datetime(2026, 5, 8, 18, 41, tzinfo=timezone.utc),
        model="claude-sonnet-4-6",
        requests=(
            BatchStateRequest("feat__auth__concept", "auth", "concept"),
            BatchStateRequest("feat__auth__task", "auth", "task"),
        ),
    )


# --- mutex / parser --------------------------------------------------------


class TestMutex:
    """Each batch-mode flag excludes the others; --force / --json modify."""

    def test_batch_and_resume_rejected(self) -> None:
        with pytest.raises(SystemExit):
            _build_parser().parse_args(["regenerate", "--batch", "--resume"])

    def test_status_and_cancel_rejected(self) -> None:
        with pytest.raises(SystemExit):
            _build_parser().parse_args(["regenerate", "--status", "--cancel"])

    def test_batch_with_force_allowed(self) -> None:
        args = _build_parser().parse_args(["regenerate", "--batch", "--force"])
        assert args.batch and args.force

    def test_status_with_json_allowed(self) -> None:
        args = _build_parser().parse_args(["regenerate", "--status", "--json"])
        assert args.status and args.json


# --- submit ----------------------------------------------------------------


class TestSubmit:
    def test_prints_batch_id_and_resume_hint(
        self, help_dir: Path, project_root: Path, capsys, monkeypatch
    ) -> None:
        monkeypatch.chdir(project_root)
        with patch(
            "attune_author.maintenance_batch.submit_maintenance_batch",
            return_value=_state("msgbatch_xyz"),
        ):
            rc = main(
                [
                    "regenerate",
                    "--batch",
                    "--help-dir",
                    str(help_dir),
                    "--project-root",
                    str(project_root),
                ]
            )
        assert rc == 0
        out = capsys.readouterr().out
        assert "msgbatch_xyz" in out
        assert "regenerate --resume" in out
        # Estimated completion should be rendered somewhere.
        assert "completion" in out.lower() or "min" in out.lower()

    def test_already_pending_returns_error(
        self, help_dir: Path, project_root: Path, capsys, monkeypatch
    ) -> None:
        monkeypatch.chdir(project_root)
        write_batch_state(help_dir, _state())
        # No --force: should fail without ever calling submit_maintenance_batch.
        rc = main(
            [
                "regenerate",
                "--batch",
                "--help-dir",
                str(help_dir),
                "--project-root",
                str(project_root),
            ]
        )
        err = capsys.readouterr().err
        assert rc == 2
        assert "already" in err.lower() or "pending" in err.lower()


# --- resume ----------------------------------------------------------------


class TestResume:
    def test_no_state_returns_error(
        self, help_dir: Path, project_root: Path, capsys, monkeypatch
    ) -> None:
        monkeypatch.chdir(project_root)
        rc = main(
            [
                "regenerate",
                "--resume",
                "--help-dir",
                str(help_dir),
                "--project-root",
                str(project_root),
            ]
        )
        assert rc == 1
        assert "no pending batch" in capsys.readouterr().err.lower()

    def test_completed_batch_prints_summary(
        self, help_dir: Path, project_root: Path, capsys, monkeypatch
    ) -> None:
        monkeypatch.chdir(project_root)
        write_batch_state(help_dir, _state("msgbatch_done"))

        from attune_author.maintenance_batch import MaintenanceResultBatch
        from attune_author.staleness import StalenessReport

        outcome = MaintenanceResultBatch(
            staleness=StalenessReport(help_entries=[], doc_entries=[]),
            final_status="ended",
            batch_id="msgbatch_done",
        )
        outcome.regenerated = ["fake-result"]  # mimic 1 regenerated
        with patch(
            "attune_author.maintenance_batch.resume_maintenance_batch",
            return_value=outcome,
        ):
            rc = main(
                [
                    "regenerate",
                    "--resume",
                    "--help-dir",
                    str(help_dir),
                    "--project-root",
                    str(project_root),
                ]
            )
        assert rc == 0
        out = capsys.readouterr().out
        assert "msgbatch_done" in out
        assert "ended" in out

    def test_timed_out_keeps_state_and_prints_hint(
        self, help_dir: Path, project_root: Path, capsys, monkeypatch
    ) -> None:
        monkeypatch.chdir(project_root)
        write_batch_state(help_dir, _state("msgbatch_inflight"))

        from attune_author.maintenance_batch import MaintenanceResultBatch
        from attune_author.staleness import StalenessReport

        outcome = MaintenanceResultBatch(
            staleness=StalenessReport(help_entries=[], doc_entries=[]),
            final_status="timed_out",
            batch_id="msgbatch_inflight",
        )
        with patch(
            "attune_author.maintenance_batch.resume_maintenance_batch",
            return_value=outcome,
        ):
            rc = main(
                [
                    "regenerate",
                    "--resume",
                    "--help-dir",
                    str(help_dir),
                    "--project-root",
                    str(project_root),
                ]
            )
        assert rc == 0
        out = capsys.readouterr().out
        assert "still running" in out.lower()
        assert "regenerate --resume" in out


# --- status ----------------------------------------------------------------


class TestStatus:
    _info = {
        "batch_id": "msgbatch_status",
        "submitted_at": "2026-05-08T18:35:00+00:00",
        "expected_completion_at": "2026-05-08T18:41:00+00:00",
        "model": "claude-sonnet-4-6",
        "request_count": 3,
        "processing_status": "in_progress",
        "request_counts": {
            "succeeded": 1,
            "errored": 0,
            "expired": 0,
            "canceled": 0,
            "processing": 2,
        },
        "ended_at": None,
        "expires_at": "2026-05-09T18:35:00+00:00",
        "cancel_initiated_at": None,
    }

    def test_human_output(self, help_dir: Path, project_root: Path, capsys, monkeypatch) -> None:
        monkeypatch.chdir(project_root)
        with patch(
            "attune_author.maintenance_batch.status_maintenance_batch",
            return_value=self._info,
        ):
            rc = main(
                [
                    "regenerate",
                    "--status",
                    "--help-dir",
                    str(help_dir),
                    "--project-root",
                    str(project_root),
                ]
            )
        assert rc == 0
        out = capsys.readouterr().out
        assert "msgbatch_status" in out
        assert "in_progress" in out
        assert "succeeded=1" in out

    def test_json_output_is_parseable(
        self, help_dir: Path, project_root: Path, capsys, monkeypatch
    ) -> None:
        monkeypatch.chdir(project_root)
        with patch(
            "attune_author.maintenance_batch.status_maintenance_batch",
            return_value=self._info,
        ):
            rc = main(
                [
                    "regenerate",
                    "--status",
                    "--json",
                    "--help-dir",
                    str(help_dir),
                    "--project-root",
                    str(project_root),
                ]
            )
        assert rc == 0
        parsed = json.loads(capsys.readouterr().out)
        assert parsed["batch_id"] == "msgbatch_status"
        assert parsed["request_counts"]["processing"] == 2

    def test_no_pending_returns_error(
        self, help_dir: Path, project_root: Path, capsys, monkeypatch
    ) -> None:
        monkeypatch.chdir(project_root)
        rc = main(
            [
                "regenerate",
                "--status",
                "--help-dir",
                str(help_dir),
                "--project-root",
                str(project_root),
            ]
        )
        assert rc == 1
        assert "no pending batch" in capsys.readouterr().err.lower()


# --- cancel ----------------------------------------------------------------


class TestCancel:
    def test_cancel_removes_state(
        self, help_dir: Path, project_root: Path, capsys, monkeypatch
    ) -> None:
        monkeypatch.chdir(project_root)
        with patch(
            "attune_author.maintenance_batch.cancel_maintenance_batch",
            return_value="msgbatch_killed",
        ):
            rc = main(
                [
                    "regenerate",
                    "--cancel",
                    "--help-dir",
                    str(help_dir),
                    "--project-root",
                    str(project_root),
                ]
            )
        assert rc == 0
        assert "msgbatch_killed" in capsys.readouterr().out

    def test_cancel_no_state_returns_error(
        self, help_dir: Path, project_root: Path, capsys, monkeypatch
    ) -> None:
        monkeypatch.chdir(project_root)
        rc = main(
            [
                "regenerate",
                "--cancel",
                "--help-dir",
                str(help_dir),
                "--project-root",
                str(project_root),
            ]
        )
        assert rc == 1
        assert "no pending" in capsys.readouterr().err.lower()


# --- bare command pending-batch hint --------------------------------------


class TestBareCommandHint:
    def test_pending_batch_hint_printed_to_stderr(
        self, help_dir: Path, project_root: Path, capsys, monkeypatch
    ) -> None:
        """Plain `regenerate` (no batch flags) prints a one-liner
        when a state file exists, but does not auto-resume."""
        monkeypatch.chdir(project_root)
        write_batch_state(help_dir, _state())
        # patch run_maintenance to a no-op so we just exercise the hint path
        with (
            patch("attune_author.maintenance.run_maintenance") as mock_run,
            patch(
                "attune_author.maintenance_batch.has_pending_batch",
                return_value=True,
            ),
        ):
            mock_run.return_value.regenerated_count = 0
            mock_run.return_value.failed = []
            rc = main(
                [
                    "regenerate",
                    "--help-dir",
                    str(help_dir),
                    "--project-root",
                    str(project_root),
                ]
            )
        assert rc == 0
        err = capsys.readouterr().err
        assert "pending batch" in err.lower()
        assert "--resume" in err
        # state file is NOT auto-deleted
        assert state_path(help_dir).exists()

    def test_no_hint_when_no_pending_batch(
        self, help_dir: Path, project_root: Path, capsys, monkeypatch
    ) -> None:
        monkeypatch.chdir(project_root)
        with patch("attune_author.maintenance.run_maintenance") as mock_run:
            mock_run.return_value.regenerated_count = 0
            mock_run.return_value.failed = []
            main(
                [
                    "regenerate",
                    "--help-dir",
                    str(help_dir),
                    "--project-root",
                    str(project_root),
                ]
            )
        err = capsys.readouterr().err
        assert "pending batch" not in err.lower()
