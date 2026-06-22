"""Prompt-cache ``cache_control`` marker resolution.

Both Anthropic emit paths (:mod:`._anthropic` synchronous calls and
:mod:`._anthropic_batch` batched calls) attach an ephemeral
``cache_control`` marker to the cached system prompt. This module is
the single place that decides the marker's shape so the two stay in
lockstep.

``ATTUNE_AUTHOR_CACHE_TTL=1h`` extends the prompt-cache window from the
5-minute default to 1 hour by adding ``"ttl": "1h"`` to the marker. Any
other value (including unset, ``5m``, or an unrecognized string) yields
the bare ephemeral marker, byte-identical to the prior behavior.
"""

from __future__ import annotations

import os


def cache_control() -> dict[str, str]:
    """Resolve the ephemeral ``cache_control`` marker from the environment.

    Read on every call (not memoized) so tests can flip the env var
    via ``monkeypatch.setenv`` and callers pick up the change without
    a process restart.

    Returns:
        ``{"type": "ephemeral", "ttl": "1h"}`` when
        ``ATTUNE_AUTHOR_CACHE_TTL`` is ``1h`` (case- and
        whitespace-insensitive); otherwise the bare
        ``{"type": "ephemeral"}`` default.
    """
    if os.getenv("ATTUNE_AUTHOR_CACHE_TTL", "5m").strip().lower() == "1h":
        return {"type": "ephemeral", "ttl": "1h"}
    return {"type": "ephemeral"}
