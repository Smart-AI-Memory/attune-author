"""Tests for the moved ``rag.corpus-info`` orchestration command.

Phase D1: this test file is the canonical pattern that D2 and D3
follow. It covers (1) the executor in isolation against a fake
pipeline, and (2) end-to-end dispatch via ``run_command`` so the
spec is verifiably registered.
"""

from __future__ import annotations

import asyncio
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from attune_author.orchestration import (
    JobContext,
    RunResult,
    list_commands,
    run_command,
)


@pytest.fixture(autouse=True)
def _import_rag_commands() -> None:
    """Importing the module triggers registration. Re-import each test
    so registry state is consistent even if a peer test cleared it."""
    sys.modules.pop("attune_author.orchestration.commands.rag", None)
    import attune_author.orchestration.commands.rag  # noqa: F401


def _ctx() -> JobContext:
    return JobContext(job_id="t-1", log=lambda _line: None)


def _fake_pipeline_with(paths: list[str]) -> MagicMock:
    pipeline = MagicMock()
    pipeline.corpus.entries.return_value = iter(SimpleNamespace(path=p) for p in paths)
    return pipeline


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def test_rag_corpus_info_is_registered() -> None:
    names = [s.name for s in list_commands()]
    assert "rag.corpus-info" in names


def test_rag_corpus_info_spec_metadata() -> None:
    from attune_author.orchestration.commands.rag import _SPEC

    assert _SPEC.domain == "rag"
    assert _SPEC.cancellable is False
    assert "developer" in _SPEC.profiles


# ---------------------------------------------------------------------------
# Executor
# ---------------------------------------------------------------------------


def test_executor_summarizes_kinds(tmp_path) -> None:
    from attune_author.orchestration.commands.rag import _exec_rag_corpus_info

    pipeline = _fake_pipeline_with(["security/concept.md", "security/task.md", "memory/concept.md"])
    with patch("attune_author.orchestration.commands.rag._build_pipeline", return_value=pipeline):
        out = asyncio.run(_exec_rag_corpus_info({"project_path": str(tmp_path)}, _ctx()))

    assert out["entry_count"] == 3
    assert out["kinds"] == ["memory", "security"]
    assert "corpus_class" in out


def test_executor_handles_no_kinds_in_paths() -> None:
    from attune_author.orchestration.commands.rag import _exec_rag_corpus_info

    pipeline = _fake_pipeline_with(["loose-file.md", "another.md"])
    with patch("attune_author.orchestration.commands.rag._build_pipeline", return_value=pipeline):
        out = asyncio.run(_exec_rag_corpus_info({}, _ctx()))

    assert out["entry_count"] == 2
    assert out["kinds"] == []


# ---------------------------------------------------------------------------
# End-to-end dispatch
# ---------------------------------------------------------------------------


def test_run_command_dispatches_to_rag_corpus_info(tmp_path) -> None:
    pipeline = _fake_pipeline_with(["a/x.md", "b/y.md"])
    with patch("attune_author.orchestration.commands.rag._build_pipeline", return_value=pipeline):

        async def go() -> RunResult:
            return await run_command("rag.corpus-info", {"project_path": str(tmp_path)}, _ctx())

        result = asyncio.run(go())

    assert isinstance(result, RunResult)
    assert result.success is True
    assert result.output["entry_count"] == 2
    assert result.output["kinds"] == ["a", "b"]
    assert result.elapsed_ms >= 0


def test_run_command_streams_log_line() -> None:
    seen: list[str] = []
    ctx = JobContext(job_id="logtest", log=seen.append)
    pipeline = _fake_pipeline_with(["x/y.md"])

    async def go() -> None:
        await run_command("rag.corpus-info", {}, ctx)

    with patch("attune_author.orchestration.commands.rag._build_pipeline", return_value=pipeline):
        asyncio.run(go())

    assert any("entries across" in line for line in seen)
