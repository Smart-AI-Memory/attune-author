"""Process-global command registry.

Phase C ships an empty registry. Phases D1–D3 fill it by importing
``attune_author.orchestration.commands.{rag,author,help}``, which
each call :func:`register` on the specs they own. The shape of
:class:`CommandSpec` mirrors attune-gui's existing dataclass so the
moves stay mechanical: copy the spec, update the ``executor`` import,
swap ``COMMANDS[name] = ...`` for ``register(...)``.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

from attune_author.orchestration.context import JobContext

ExecutorFn = Callable[[dict[str, Any], JobContext], Awaitable[Any]]


@dataclass(frozen=True)
class CommandSpec:
    """Static description of a runnable command.

    Mirrors ``attune_gui.commands.CommandSpec`` field-for-field so the
    Phase D migrations are a copy with an import-path edit. The shape
    is frozen because specs are registered once at import time and
    consulted from many call sites; mutation would be a footgun.
    """

    name: str
    title: str
    domain: str
    description: str
    args_schema: dict[str, Any]
    executor: ExecutorFn
    cancellable: bool = True
    profiles: tuple[str, ...] = field(default=("developer",))


COMMANDS: dict[str, CommandSpec] = {}


def register(spec: CommandSpec) -> None:
    """Add ``spec`` to the global registry.

    Re-registering the same name overwrites the previous spec. That's
    intentional: tests and downstream packages routinely
    monkey-patch a command in place. If overwrite ever needs to be
    an error condition, callers can check ``spec.name in COMMANDS``
    themselves.
    """

    COMMANDS[spec.name] = spec


def list_commands() -> list[CommandSpec]:
    """Snapshot of currently-registered specs, sorted by name."""

    return sorted(COMMANDS.values(), key=lambda s: s.name)
