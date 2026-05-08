"""Tests for the moved ``help.*`` orchestration commands.

Phase D3. attune-help is mocked at its import site so the test does
not depend on the real ``HelpEngine`` rendering pipeline (covered
in attune-help's own tests).
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from attune_author.orchestration import (
    JobContext,
    ValidationError,
    list_commands,
    run_command,
)


@pytest.fixture(autouse=True)
def _import_help_commands():
    sys.modules.pop("attune_author.orchestration.commands.help", None)
    import attune_author.orchestration.commands.help  # noqa: F401


def _ctx() -> JobContext:
    return JobContext(job_id="t-1", log=lambda _line: None)


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def test_three_help_commands_registered() -> None:
    names = {s.name for s in list_commands()}
    expected = {"help.lookup", "help.search", "help.list"}
    assert expected.issubset(names), names


def test_help_specs_metadata() -> None:
    from attune_author.orchestration.commands.help import (
        _LIST_SPEC,
        _LOOKUP_SPEC,
        _SEARCH_SPEC,
    )

    for spec in (_LOOKUP_SPEC, _SEARCH_SPEC, _LIST_SPEC):
        assert spec.domain == "help"
        assert spec.cancellable is False
        assert "developer" in spec.profiles


# ---------------------------------------------------------------------------
# help.lookup
# ---------------------------------------------------------------------------


def test_lookup_returns_content_and_total_topics() -> None:
    engine = MagicMock()
    engine.lookup.return_value = "concept body"
    engine.list_topics.return_value = ["a", "b", "c"]
    engine.generated_dir = Path("/tmp/help")  # noqa: S108

    with patch("attune_help.HelpEngine", return_value=engine):

        async def go():
            return await run_command("help.lookup", {"topic": "auth", "depth": "concept"}, _ctx())

        result = asyncio.run(go())

    assert result.output["topic"] == "auth"
    assert result.output["depth"] == "concept"
    assert result.output["content"] == "concept body"
    assert result.output["total_topics"] == 3


def test_lookup_walks_progressive_depth() -> None:
    """depth=reference should call HelpEngine.lookup three times."""
    engine = MagicMock()
    engine.lookup.return_value = "body"
    engine.list_topics.return_value = []
    engine.generated_dir = Path("/tmp/help")  # noqa: S108

    with patch("attune_help.HelpEngine", return_value=engine):

        async def go():
            await run_command("help.lookup", {"topic": "x", "depth": "reference"}, _ctx())

        asyncio.run(go())

    assert engine.lookup.call_count == 3


def test_lookup_missing_topic_raises_validation_error() -> None:
    engine = MagicMock()
    engine.lookup.return_value = None

    with patch("attune_help.HelpEngine", return_value=engine):

        async def go():
            await run_command("help.lookup", {"topic": "ghost"}, _ctx())

        with pytest.raises(ValidationError):
            asyncio.run(go())


def test_lookup_requires_topic() -> None:
    async def go():
        await run_command("help.lookup", {}, _ctx())

    with pytest.raises(ValidationError):
        asyncio.run(go())


# ---------------------------------------------------------------------------
# help.search
# ---------------------------------------------------------------------------


def test_search_returns_results_with_count() -> None:
    engine = MagicMock()
    engine.search.return_value = [("topic-a", 0.9), ("topic-b", 0.5)]
    engine.generated_dir = Path("/tmp/help")  # noqa: S108

    with patch("attune_help.HelpEngine", return_value=engine):

        async def go():
            return await run_command("help.search", {"query": "auth", "limit": 5}, _ctx())

        result = asyncio.run(go())

    assert result.output["count"] == 2
    assert len(result.output["results"]) == 2
    engine.search.assert_called_once_with("auth", limit=5)


def test_search_requires_query() -> None:
    async def go():
        await run_command("help.search", {}, _ctx())

    with pytest.raises(ValidationError):
        asyncio.run(go())


# ---------------------------------------------------------------------------
# help.list
# ---------------------------------------------------------------------------


def test_list_returns_topics_with_type_filter() -> None:
    engine = MagicMock()
    engine.list_topics.return_value = ["alpha", "beta"]
    engine.generated_dir = Path("/tmp/help")  # noqa: S108

    with patch("attune_help.HelpEngine", return_value=engine):

        async def go():
            return await run_command("help.list", {"type_filter": "concepts"}, _ctx())

        result = asyncio.run(go())

    assert result.output["count"] == 2
    assert result.output["type_filter"] == "concepts"
    engine.list_topics.assert_called_once_with(type_filter="concepts")


def test_list_blank_filter_passes_none() -> None:
    engine = MagicMock()
    engine.list_topics.return_value = ["x"]
    engine.generated_dir = Path("/tmp/help")  # noqa: S108

    with patch("attune_help.HelpEngine", return_value=engine):

        async def go():
            return await run_command("help.list", {}, _ctx())

        result = asyncio.run(go())

    assert result.output["type_filter"] is None
    engine.list_topics.assert_called_once_with(type_filter=None)


# ---------------------------------------------------------------------------
# Lazy attune-help import
# ---------------------------------------------------------------------------


def test_help_engine_raises_validation_error_when_attune_help_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """If attune-help is not importable, the executor surfaces a clear error."""

    if isinstance(__builtins__, dict):  # type: ignore[index]
        real_import = __builtins__["__import__"]  # type: ignore[index]
    else:
        real_import = __builtins__.__import__

    def fake_import(name, *args, **kwargs):
        if name == "attune_help":
            raise ImportError("no attune_help in this environment")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", fake_import)

    from attune_author.orchestration.commands.help import _help_engine

    with pytest.raises(ValidationError, match="attune-help is not installed"):
        _help_engine(None, "job-1")
