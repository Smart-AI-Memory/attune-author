"""Tests for the batched maintenance flow.

Covers:

- State file lifecycle (write/read/delete, schema, retention)
- ``submit_maintenance_batch`` happy path + multiple-batch guard
- ``resume_maintenance_batch`` happy path, partial-failure
  isolation per feature, and timeout-keeps-state semantics
- ``status_maintenance_batch`` shape
- ``cancel_maintenance_batch`` cleanup
- **Parity**: same stale features → same on-disk template
  files, regardless of synchronous vs batch path

The Anthropic SDK is stubbed at the
``attune_author.doc_gen._anthropic_batch.{submit_batch,
poll_batch}`` boundary so no live calls leave the test process.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from attune_author.doc_gen._anthropic_batch import (
    BatchPolishRequest,
    BatchPolishResult,
)
from attune_author.maintenance_batch import (
    BatchAlreadyPending,
    BatchState,
    BatchStateExpired,
    BatchStateNotFound,
    BatchStateRequest,
    MaintenanceResultBatch,
    cancel_maintenance_batch,
    custom_id_for,
    delete_batch_state,
    has_pending_batch,
    read_batch_state,
    resume_maintenance_batch,
    state_path,
    status_maintenance_batch,
    submit_maintenance_batch,
    write_batch_state,
)

# --- helpers ---------------------------------------------------------------


def _state(submitted_at: datetime | None = None) -> BatchState:
    return BatchState(
        schema_version=1,
        batch_id="msgbatch_test",
        submitted_at=submitted_at or datetime(2026, 5, 8, 18, 35, tzinfo=timezone.utc),
        expected_completion_at=datetime(2026, 5, 8, 18, 41, tzinfo=timezone.utc),
        model="claude-sonnet-4-20250514",
        requests=(
            BatchStateRequest("feat__auth__concept", "auth", "concept"),
            BatchStateRequest("feat__auth__task", "auth", "task"),
            BatchStateRequest("feat__auth__reference", "auth", "reference"),
        ),
    )


def _stub_succeeded_results(features_and_depths: list[tuple[str, str]]) -> list[BatchPolishResult]:
    """Build a successful batch result for each (feature, depth)."""
    return [
        BatchPolishResult(
            custom_id=custom_id_for(f, d),
            feature=f,
            depth=d,
            text=f"# polished {f}/{d}\n\npolished body for {f} at depth {d}.\n",
            error=None,
        )
        for f, d in features_and_depths
    ]


# --- state file lifecycle --------------------------------------------------


class TestStateFile:
    def test_round_trip_preserves_all_fields(self, tmp_path: Path) -> None:
        s = _state()
        write_batch_state(tmp_path, s)
        loaded = read_batch_state(tmp_path, now=datetime(2026, 5, 9, tzinfo=timezone.utc))
        assert loaded == s

    def test_state_path_uses_dotfile(self, tmp_path: Path) -> None:
        assert state_path(tmp_path).name == ".batch-state.json"

    def test_has_pending_batch_false_when_no_state(self, tmp_path: Path) -> None:
        assert has_pending_batch(tmp_path) is False

    def test_has_pending_batch_true_after_write(self, tmp_path: Path) -> None:
        write_batch_state(tmp_path, _state())
        assert has_pending_batch(tmp_path) is True

    def test_delete_state_no_op_when_missing(self, tmp_path: Path) -> None:
        delete_batch_state(tmp_path)  # should not raise

    def test_read_raises_not_found_when_missing(self, tmp_path: Path) -> None:
        with pytest.raises(BatchStateNotFound):
            read_batch_state(tmp_path)

    def test_read_raises_expired_for_old_state(self, tmp_path: Path) -> None:
        old = _state(submitted_at=datetime(2026, 1, 1, tzinfo=timezone.utc))
        write_batch_state(tmp_path, old)
        with pytest.raises(BatchStateExpired, match="29-day retention"):
            read_batch_state(tmp_path, now=datetime(2026, 5, 8, tzinfo=timezone.utc))

    def test_read_raises_expired_for_unknown_schema(self, tmp_path: Path) -> None:
        target = state_path(tmp_path)
        target.write_text(
            json.dumps(
                {
                    "schema_version": 999,
                    "batch_id": "x",
                    "submitted_at": "2026-05-08T18:35:00+00:00",
                    "expected_completion_at": "2026-05-08T18:41:00+00:00",
                    "model": "m",
                    "requests": [],
                }
            )
        )
        with pytest.raises(BatchStateExpired, match="schema_version"):
            read_batch_state(tmp_path)

    def test_read_raises_expired_for_corrupt_json(self, tmp_path: Path) -> None:
        state_path(tmp_path).write_text("not json {")
        with pytest.raises(BatchStateExpired, match="corrupt"):
            read_batch_state(tmp_path)

    def test_write_is_atomic_via_tempfile(self, tmp_path: Path) -> None:
        write_batch_state(tmp_path, _state())
        # No leftover .tmp file after a successful write.
        assert not list(tmp_path.glob("*.tmp"))
        assert state_path(tmp_path).exists()


# --- submit ----------------------------------------------------------------


class TestSubmit:
    def test_raises_when_state_already_exists(self, help_dir: Path, project_root: Path) -> None:
        write_batch_state(help_dir, _state())
        with pytest.raises(BatchAlreadyPending):
            submit_maintenance_batch(help_dir, project_root)

    def test_force_overwrites_existing_state(self, help_dir: Path, project_root: Path) -> None:
        write_batch_state(help_dir, _state())
        with patch("attune_author.maintenance_batch.submit_batch", return_value="msgbatch_new"):
            new_state = submit_maintenance_batch(
                help_dir, project_root, force=True, client=MagicMock()
            )
        assert new_state.batch_id == "msgbatch_new"

    def test_submit_writes_state_file_with_request_manifest(
        self, help_dir: Path, project_root: Path
    ) -> None:
        with patch("attune_author.maintenance_batch.submit_batch", return_value="msgbatch_aaa"):
            submitted = submit_maintenance_batch(help_dir, project_root, client=MagicMock())
        assert submitted.batch_id == "msgbatch_aaa"
        assert has_pending_batch(help_dir)
        # Every request in state has a (feature, depth) we can map back.
        assert all(r.custom_id.startswith("feat__") for r in submitted.requests)
        # Persisted file matches the in-memory state. Read with ``now`` set
        # to the submit timestamp so the 29-day retention check doesn't fire
        # on the fresh state file we just wrote.
        loaded = read_batch_state(help_dir, now=submitted.submitted_at)
        assert loaded.batch_id == submitted.batch_id

    def test_submit_passes_polish_requests_to_submit_batch(
        self, help_dir: Path, project_root: Path
    ) -> None:
        captured: list[BatchPolishRequest] = []

        def _capture(reqs, client=None):  # noqa: ARG001
            captured.extend(reqs)
            return "msgbatch_captured"

        with patch("attune_author.maintenance_batch.submit_batch", side_effect=_capture):
            submit_maintenance_batch(help_dir, project_root, client=MagicMock())
        assert len(captured) > 0
        # Each captured request has a non-empty system + user_message
        # (build_polish_prompt produced real content) and a custom_id
        # matching feat__{feature}__{depth}.
        for r in captured:
            assert r.system.strip()
            assert r.user_message.strip()
            assert r.custom_id == custom_id_for(r.feature, r.depth)

    def test_submit_raises_when_no_stale_features(self, help_dir: Path, project_root: Path) -> None:
        # Run normal maintain first so everything is current.
        from attune_author.maintenance import run_maintenance

        run_maintenance(help_dir=help_dir, project_root=project_root)
        with pytest.raises(ValueError, match="no stale features"):
            submit_maintenance_batch(help_dir, project_root, client=MagicMock())


# --- resume ----------------------------------------------------------------


class TestResume:
    def _seed_state_for(self, help_dir: Path, project_root: Path) -> BatchState:
        with patch(
            "attune_author.maintenance_batch.submit_batch",
            return_value="msgbatch_resume_test",
        ):
            return submit_maintenance_batch(help_dir, project_root, client=MagicMock())

    def test_resume_writes_polished_templates_for_successful_features(
        self, help_dir: Path, project_root: Path
    ) -> None:
        state = self._seed_state_for(help_dir, project_root)
        results = _stub_succeeded_results([(r.feature, r.depth) for r in state.requests])
        with patch(
            "attune_author.maintenance_batch.poll_batch",
            return_value=("ended", results),
        ):
            outcome = resume_maintenance_batch(help_dir, project_root, client=MagicMock())
        assert isinstance(outcome, MaintenanceResultBatch)
        assert outcome.final_status == "ended"
        assert outcome.regenerated_count >= 1
        assert outcome.failed == []
        # State file was deleted after successful resume.
        assert not has_pending_batch(help_dir)
        # On-disk file actually contains the polished body.
        regenerated_paths = [t.path for r in outcome.regenerated for t in r.templates]
        for path in regenerated_paths:
            assert "polished body" in path.read_text(encoding="utf-8")

    def test_resume_isolates_per_feature_failure(self, help_dir: Path, project_root: Path) -> None:
        state = self._seed_state_for(help_dir, project_root)
        results: list[BatchPolishResult] = []
        for r in state.requests:
            if r.feature == "auth" and r.depth == "concept":
                # One failed depth fails the whole feature.
                results.append(
                    BatchPolishResult(
                        custom_id=r.custom_id,
                        feature=r.feature,
                        depth=r.depth,
                        text=None,
                        error="rate_limit_error",
                    )
                )
            else:
                results.append(
                    BatchPolishResult(
                        custom_id=r.custom_id,
                        feature=r.feature,
                        depth=r.depth,
                        text=f"# polished {r.feature}/{r.depth}\n",
                        error=None,
                    )
                )
        with patch(
            "attune_author.maintenance_batch.poll_batch",
            return_value=("ended", results),
        ):
            outcome = resume_maintenance_batch(help_dir, project_root, client=MagicMock())
        assert "auth" in outcome.failed
        # State file deleted on terminal completion (even with failures).
        assert not has_pending_batch(help_dir)

    def test_resume_timeout_keeps_state_file(self, help_dir: Path, project_root: Path) -> None:
        state = self._seed_state_for(help_dir, project_root)
        timed = [
            BatchPolishResult(
                custom_id=r.custom_id,
                feature=r.feature,
                depth=r.depth,
                text=None,
                error="timed_out",
            )
            for r in state.requests
        ]
        with patch(
            "attune_author.maintenance_batch.poll_batch",
            return_value=("timed_out", timed),
        ):
            outcome = resume_maintenance_batch(help_dir, project_root, client=MagicMock())
        assert outcome.final_status == "timed_out"
        # State file retained for next --resume invocation.
        assert has_pending_batch(help_dir)


# --- status & cancel -------------------------------------------------------


class TestStatus:
    def test_status_returns_local_state_plus_anthropic_view(
        self, help_dir: Path, project_root: Path
    ) -> None:
        write_batch_state(help_dir, _state())
        client = MagicMock()
        client.messages.batches.retrieve.return_value = SimpleNamespace(
            processing_status="in_progress",
            request_counts=SimpleNamespace(
                succeeded=1, errored=0, expired=0, canceled=0, processing=2
            ),
            ended_at=None,
            expires_at="2026-05-09T18:35:00Z",
            cancel_initiated_at=None,
        )
        out = status_maintenance_batch(help_dir, client=client)
        assert out["batch_id"] == "msgbatch_test"
        assert out["processing_status"] == "in_progress"
        assert out["request_counts"]["processing"] == 2
        assert out["request_count"] == 3
        # JSON-serializable for cron consumers
        json.dumps(out)


class TestCancel:
    def test_cancel_removes_state_file_and_calls_sdk(
        self, help_dir: Path, project_root: Path
    ) -> None:
        write_batch_state(help_dir, _state())
        client = MagicMock()
        cancel_maintenance_batch(help_dir, client=client)
        client.messages.batches.cancel.assert_called_once_with("msgbatch_test")
        assert not has_pending_batch(help_dir)

    def test_cancel_removes_state_even_when_sdk_fails(
        self, help_dir: Path, project_root: Path
    ) -> None:
        write_batch_state(help_dir, _state())
        client = MagicMock()
        client.messages.batches.cancel.side_effect = RuntimeError("network down")
        cancel_maintenance_batch(help_dir, client=client)
        assert not has_pending_batch(help_dir)


# --- parity ----------------------------------------------------------------


class TestParity:
    def test_synchronous_and_batch_paths_write_same_file_set(
        self, help_dir: Path, project_root: Path
    ) -> None:
        """Same stale features → same set of template files written.

        Guards against drift between the two paths' rendering. The
        actual *content* differs because the polish pass is mocked
        in the batch path; we assert the set of files and their
        ``feature/depth`` shape match.
        """
        from attune_author.maintenance import run_maintenance

        # --- synchronous run ---
        sync_dir = help_dir.parent / ".help_sync"
        sync_dir.mkdir()
        (sync_dir / "features.yaml").write_text(
            (help_dir / "features.yaml").read_text(),
            encoding="utf-8",
        )
        sync_outcome = run_maintenance(help_dir=sync_dir, project_root=project_root)
        sync_paths = {
            t.path.relative_to(sync_dir).as_posix()
            for r in sync_outcome.regenerated
            for t in r.templates
        }

        # --- batch run ---
        with patch(
            "attune_author.maintenance_batch.submit_batch",
            return_value="msgbatch_parity",
        ):
            state = submit_maintenance_batch(help_dir, project_root, client=MagicMock())

        results = _stub_succeeded_results([(r.feature, r.depth) for r in state.requests])
        with patch(
            "attune_author.maintenance_batch.poll_batch",
            return_value=("ended", results),
        ):
            batch_outcome = resume_maintenance_batch(help_dir, project_root, client=MagicMock())
        batch_paths = {
            t.path.relative_to(help_dir).as_posix()
            for r in batch_outcome.regenerated
            for t in r.templates
        }
        assert sync_paths == batch_paths
