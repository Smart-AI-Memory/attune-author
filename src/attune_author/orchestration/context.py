"""Per-job context and result types.

:class:`JobContext` is the slim contract every command executor sees.
It deliberately doesn't reach into any host's job-tracking object —
attune-gui can wrap its own ``Job`` to satisfy this shape, while a
CLI caller can build one with ``log=print`` and an unset event.

:class:`RunResult` is what ``run_command`` returns once an executor
finishes successfully.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class JobContext:
    """Streaming side channel handed to a command executor.

    Attributes:
        job_id: Stable identifier for the run. Hosts that don't track
            jobs (CLI invocations, tests) can use any unique string.
        log: Single-line log emitter. Implementations push to whatever
            sink the host wants (gui job buffer, stdout, structlog).
        cancel_event: Cooperative cancellation flag. Executors poll
            ``ctx.cancel_event.is_set()`` between work units and bail
            out cleanly when set. A default unset event is created
            when none is supplied so simple callers don't have to
            think about it.
    """

    job_id: str
    log: Callable[[str], None]
    cancel_event: threading.Event = field(default_factory=threading.Event)


@dataclass(frozen=True)
class RunResult:
    """Successful command outcome returned from ``run_command``.

    Attributes:
        success: Always ``True`` for a returned ``RunResult``;
            failures raise :class:`OrchestrationError` (or propagate
            an unexpected exception). The flag exists so future
            extensions — partial successes, soft warnings — have a
            place without breaking the type.
        output: Executor-specific payload. Convention: JSON-friendly
            dicts/lists/scalars so attune-gui can serialize them
            unmodified.
        elapsed_ms: Wall-clock duration in milliseconds, integer for
            log-friendliness. ``run_command`` is responsible for
            populating this; executors don't measure themselves.
    """

    success: bool
    output: dict[str, Any]
    elapsed_ms: int
