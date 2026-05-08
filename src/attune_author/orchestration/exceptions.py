"""Exception hierarchy for the orchestration runtime.

All known failure modes derive from :class:`OrchestrationError`.
Anything else propagates unchanged so unexpected exceptions still
surface a stack trace instead of being swallowed.
"""

from __future__ import annotations


class OrchestrationError(Exception):
    """Base for predictable orchestration failures.

    Carries an optional short ``code`` so callers (notably
    attune-gui's error envelope) can render a stable
    machine-readable string without parsing the message.
    """

    code: str = "orchestration_error"

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        if code is not None:
            self.code = code


class CommandNotFound(OrchestrationError):
    """Raised when ``run_command`` is invoked with an unregistered name."""

    code = "command_not_found"


class ValidationError(OrchestrationError):
    """Raised when a command's ``args`` fail spec validation."""

    code = "validation_error"


class RunnerBusy(OrchestrationError):
    """Raised when the runtime cannot accept a new job right now.

    Reserved for the future single-runner dispatcher. Phase D handlers
    map this to HTTP 409 / 429 in the route layer.
    """

    code = "runner_busy"
