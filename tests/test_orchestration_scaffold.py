"""Phase C scaffold tests.

The orchestration package starts empty: types defined, registry
empty, ``run_command`` wired to dispatch but with nothing to
dispatch to. Phases D1–D3 will populate it. These tests pin the
contract so those moves stay mechanical.
"""

from __future__ import annotations

import asyncio
import threading
from typing import Any

import pytest

from attune_author.orchestration import (
    COMMANDS,
    CommandNotFound,
    CommandSpec,
    JobContext,
    OrchestrationError,
    RunResult,
    ValidationError,
    list_commands,
    register,
    run_command,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ctx(job_id: str = "t-1") -> JobContext:
    return JobContext(job_id=job_id, log=lambda _line: None)


@pytest.fixture(autouse=True)
def _clean_registry() -> None:
    """Wipe COMMANDS around each test so order can't leak state."""
    saved = dict(COMMANDS)
    COMMANDS.clear()
    yield
    COMMANDS.clear()
    COMMANDS.update(saved)


# ---------------------------------------------------------------------------
# Empty-state contract
# ---------------------------------------------------------------------------


def test_empty_registry_lists_nothing() -> None:
    assert list_commands() == []


def test_run_command_unknown_raises_command_not_found() -> None:
    async def go() -> None:
        await run_command("does.not.exist", {}, _ctx())

    with pytest.raises(CommandNotFound) as ei:
        asyncio.run(go())
    assert "does.not.exist" in str(ei.value)
    assert ei.value.code == "command_not_found"


def test_command_not_found_is_orchestration_error() -> None:
    assert issubclass(CommandNotFound, OrchestrationError)
    assert issubclass(ValidationError, OrchestrationError)


# ---------------------------------------------------------------------------
# Registration + dispatch
# ---------------------------------------------------------------------------


async def _ok_executor(args: dict[str, Any], ctx: JobContext) -> dict[str, Any]:
    ctx.log("ran")
    return {"echo": args.get("payload")}


def _spec(name: str = "test.echo") -> CommandSpec:
    return CommandSpec(
        name=name,
        title="Echo",
        domain="test",
        description="Used by scaffold tests.",
        args_schema={"type": "object"},
        executor=_ok_executor,
    )


def test_register_makes_command_visible() -> None:
    register(_spec("test.echo"))
    assert [s.name for s in list_commands()] == ["test.echo"]


def test_list_commands_sorts_by_name() -> None:
    register(_spec("z.last"))
    register(_spec("a.first"))
    register(_spec("m.middle"))
    assert [s.name for s in list_commands()] == ["a.first", "m.middle", "z.last"]


def test_run_command_returns_runresult_with_elapsed_ms() -> None:
    register(_spec())

    async def go() -> RunResult:
        return await run_command("test.echo", {"payload": 42}, _ctx())

    result = asyncio.run(go())
    assert isinstance(result, RunResult)
    assert result.success is True
    assert result.output == {"echo": 42}
    assert result.elapsed_ms >= 0


def test_run_command_wraps_non_dict_output() -> None:
    async def returns_int(args: dict[str, Any], ctx: JobContext) -> int:
        return 7

    register(
        CommandSpec(
            name="test.int",
            title="Int",
            domain="test",
            description="",
            args_schema={},
            executor=returns_int,
        )
    )

    async def go() -> RunResult:
        return await run_command("test.int", {}, _ctx())

    result = asyncio.run(go())
    assert result.output == {"value": 7}


def test_run_command_lets_validation_error_propagate() -> None:
    async def bad(args: dict[str, Any], ctx: JobContext) -> dict[str, Any]:
        raise ValidationError("missing required field 'x'")

    register(
        CommandSpec(
            name="test.bad",
            title="Bad",
            domain="test",
            description="",
            args_schema={},
            executor=bad,
        )
    )

    async def go() -> None:
        await run_command("test.bad", {}, _ctx())

    with pytest.raises(ValidationError) as ei:
        asyncio.run(go())
    assert ei.value.code == "validation_error"


def test_re_register_overwrites() -> None:
    async def v1(args: dict[str, Any], ctx: JobContext) -> dict[str, Any]:
        return {"v": 1}

    async def v2(args: dict[str, Any], ctx: JobContext) -> dict[str, Any]:
        return {"v": 2}

    register(
        CommandSpec(
            name="test.dup",
            title="",
            domain="test",
            description="",
            args_schema={},
            executor=v1,
        )
    )
    register(
        CommandSpec(
            name="test.dup",
            title="",
            domain="test",
            description="",
            args_schema={},
            executor=v2,
        )
    )

    async def go() -> RunResult:
        return await run_command("test.dup", {}, _ctx())

    assert asyncio.run(go()).output == {"v": 2}


# ---------------------------------------------------------------------------
# JobContext shape
# ---------------------------------------------------------------------------


def test_jobcontext_default_cancel_event_is_unset() -> None:
    ctx = _ctx()
    assert isinstance(ctx.cancel_event, threading.Event)
    assert not ctx.cancel_event.is_set()


def test_jobcontext_log_callable_receives_lines() -> None:
    seen: list[str] = []
    ctx = JobContext(job_id="logtest", log=seen.append)
    register(_spec("test.echo"))

    async def go() -> None:
        await run_command("test.echo", {"payload": "hi"}, ctx)

    asyncio.run(go())
    assert seen == ["ran"]
