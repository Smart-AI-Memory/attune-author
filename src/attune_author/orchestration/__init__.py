"""Orchestration runtime — the public API attune-gui (and the CLI)
will route every command invocation through.

Phase C ships the scaffold only: types, an empty registry, and an
async ``run_command`` that knows how to time and dispatch a spec but
has nothing to dispatch *to*. Phases D1–D3 of the
``architecture-realignment`` spec move the actual command bodies in
from attune-gui's ``commands.py`` and register them here.

Public surface
--------------
- :class:`CommandSpec` — declarative shape every command supplies.
- :func:`register` / :func:`list_commands` — registry helpers.
- :class:`JobContext`, :class:`RunResult` — per-call types.
- :class:`OrchestrationError` and subclasses — predictable failure
  modes; anything else bubbles up unchanged.
- :func:`run_command` — single entry point; ``await``-able.
"""

from __future__ import annotations

import time
from typing import Any

from attune_author.orchestration.context import JobContext, RunResult
from attune_author.orchestration.exceptions import (
    CommandNotFound,
    OrchestrationError,
    RunnerBusy,
    ValidationError,
)
from attune_author.orchestration.registry import (
    COMMANDS,
    CommandSpec,
    ExecutorFn,
    list_commands,
    register,
)

__all__ = [
    "COMMANDS",
    "CommandNotFound",
    "CommandSpec",
    "ExecutorFn",
    "JobContext",
    "OrchestrationError",
    "RunResult",
    "RunnerBusy",
    "ValidationError",
    "list_commands",
    "register",
    "run_command",
]


async def run_command(
    name: str,
    args: dict[str, Any],
    ctx: JobContext,
) -> RunResult:
    """Execute the registered command ``name`` with ``args`` and ``ctx``.

    The function looks up the spec, awaits its ``executor``, and
    wraps the return value in a :class:`RunResult` along with a
    wall-clock duration. Errors:

    - :class:`CommandNotFound` if no spec is registered for ``name``.
    - :class:`OrchestrationError` (or subclasses — ``ValidationError``,
      ``RunnerBusy``) re-raised unchanged when an executor signals
      a known failure mode.
    - Any other exception bubbles up so unexpected bugs surface their
      stack trace.

    The executor is responsible for argument validation; raising
    ``ValidationError`` is the conventional way to report bad input.
    """

    spec = COMMANDS.get(name)
    if spec is None:
        raise CommandNotFound(f"unknown command: {name!r}")

    started = time.monotonic()
    output = await spec.executor(args, ctx)
    elapsed_ms = int((time.monotonic() - started) * 1000)

    if not isinstance(output, dict):
        output = {"value": output}
    return RunResult(success=True, output=output, elapsed_ms=elapsed_ms)
