"""Cache-TTL wire-shape tests for the Anthropic doc-gen emit paths.

``ATTUNE_AUTHOR_CACHE_TTL=1h`` extends the prompt-cache window from the
5-minute default to 1 hour by adding ``"ttl": "1h"`` to the
``cache_control`` marker on the cached system prompt. These tests lock
the wire shape at both emit sites — the synchronous
``call_anthropic`` path and the batched ``_build_request_param`` path —
for the default and the 1h value, mocking the client (no live API).

Mirrors ``attune-rag``'s ``test_claude_cache_ttl.py``. The default-shape
regressions also live in ``test_anthropic_retry.py`` (``TestCacheSystem``)
and ``test_anthropic_batch.py``; this file covers the env-driven 1h shape
and the helper itself.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from attune_author.doc_gen._anthropic import call_anthropic
from attune_author.doc_gen._anthropic_batch import (
    BatchPolishRequest,
    _build_request_param,
)
from attune_author.doc_gen._cache import cache_control

_EPHEMERAL = {"type": "ephemeral"}
_EPHEMERAL_1H = {"type": "ephemeral", "ttl": "1h"}


# --- cache_control() helper -------------------------------------------------


@pytest.mark.parametrize(
    "value,expected",
    [
        (None, _EPHEMERAL),  # unset → default
        ("5m", _EPHEMERAL),  # explicit default
        ("1h", _EPHEMERAL_1H),  # extended
        (" 1H ", _EPHEMERAL_1H),  # case + whitespace insensitive
        ("30m", _EPHEMERAL),  # unsupported value → safe default
        ("", _EPHEMERAL),  # empty → default
    ],
)
def test_cache_control_resolves_from_env(
    monkeypatch: pytest.MonkeyPatch, value: str | None, expected: dict
) -> None:
    if value is None:
        monkeypatch.delenv("ATTUNE_AUTHOR_CACHE_TTL", raising=False)
    else:
        monkeypatch.setenv("ATTUNE_AUTHOR_CACHE_TTL", value)
    assert cache_control() == expected


def _ok_response(text: str) -> MagicMock:
    block = MagicMock()
    block.text = text
    response = MagicMock()
    response.content = [block]
    return response


# --- synchronous call_anthropic emit site -----------------------------------


def test_sync_system_carries_1h_ttl(monkeypatch: pytest.MonkeyPatch) -> None:
    """With ATTUNE_AUTHOR_CACHE_TTL=1h the cached system block carries the
    extended marker."""
    monkeypatch.setenv("ATTUNE_AUTHOR_CACHE_TTL", "1h")

    client = MagicMock()
    client.messages.create.return_value = _ok_response("ok")

    call_anthropic(
        client,
        system="big prompt",
        user_message="u",
        model="m",
        max_tokens=10,
        cache_system=True,
    )

    system = client.messages.create.call_args.kwargs["system"]
    assert system[0]["cache_control"] == _EPHEMERAL_1H


def test_sync_system_defaults_to_5m(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unset env → the system marker is byte-identical to the prior default."""
    monkeypatch.delenv("ATTUNE_AUTHOR_CACHE_TTL", raising=False)

    client = MagicMock()
    client.messages.create.return_value = _ok_response("ok")

    call_anthropic(
        client,
        system="big prompt",
        user_message="u",
        model="m",
        max_tokens=10,
        cache_system=True,
    )

    system = client.messages.create.call_args.kwargs["system"]
    assert system[0]["cache_control"] == _EPHEMERAL


# --- batched _build_request_param emit site ---------------------------------


def _req() -> BatchPolishRequest:
    return BatchPolishRequest(
        custom_id="feat__x__concept",
        feature="x",
        depth="concept",
        system="big prompt",
        user_message="u",
        model="m",
        max_tokens=10,
        cache_system=True,
    )


def test_batch_system_carries_1h_ttl(monkeypatch: pytest.MonkeyPatch) -> None:
    """With 1h set, the batched system block carries the extended marker."""
    monkeypatch.setenv("ATTUNE_AUTHOR_CACHE_TTL", "1h")
    param = _build_request_param(_req())
    system = param["params"]["system"]
    assert system[0]["cache_control"] == _EPHEMERAL_1H


def test_batch_system_defaults_to_5m(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unset env → batched system marker is byte-identical to the prior default."""
    monkeypatch.delenv("ATTUNE_AUTHOR_CACHE_TTL", raising=False)
    param = _build_request_param(_req())
    system = param["params"]["system"]
    assert system[0]["cache_control"] == _EPHEMERAL
