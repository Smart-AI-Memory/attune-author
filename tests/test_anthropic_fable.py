"""Fable-model handling in the shared Anthropic chokepoint.

Mock-only (per testing-conventions.md): verifies call_anthropic routes
claude-fable* models through the beta namespace with the server-side
fallback kwargs, raises ModelRefusalError on stop_reason == "refusal",
and appends the retention hint to a 400 — while non-fable models keep
the exact pre-tier wire payload.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from attune_author.doc_gen._anthropic import AnthropicCallError, call_anthropic
from attune_author.model_tiers import ModelRefusalError


def _response(text: str = "out", stop_reason: str = "end_turn") -> SimpleNamespace:
    return SimpleNamespace(
        content=[SimpleNamespace(text=text)],
        stop_reason=stop_reason,
        usage=None,
    )


def test_fable_routes_to_beta_namespace_with_extras() -> None:
    client = MagicMock()
    client.beta.messages.create.return_value = _response("polished")
    result = call_anthropic(
        client,
        system="s",
        user_message="u",
        model="claude-fable-5",
        max_tokens=64,
    )
    assert result == "polished"
    client.messages.create.assert_not_called()
    kwargs = client.beta.messages.create.call_args.kwargs
    assert kwargs["betas"] == ["server-side-fallback-2026-06-01"]
    assert kwargs["fallbacks"] == [{"model": "claude-opus-4-8"}]
    assert kwargs["model"] == "claude-fable-5"


def test_non_fable_keeps_plain_namespace_and_payload() -> None:
    client = MagicMock()
    client.messages.create.return_value = _response("ok")
    call_anthropic(
        client,
        system="s",
        user_message="u",
        model="claude-sonnet-5",
        max_tokens=64,
    )
    client.beta.messages.create.assert_not_called()
    kwargs = client.messages.create.call_args.kwargs
    assert "betas" not in kwargs
    assert "fallbacks" not in kwargs


def test_fable_refusal_raises_model_refusal_error_not_wrapped() -> None:
    client = MagicMock()
    refusal = _response("")
    refusal.stop_details = SimpleNamespace(category="harmful_content", explanation="no")
    refusal.stop_reason = "refusal"
    client.beta.messages.create.return_value = refusal
    with pytest.raises(ModelRefusalError) as excinfo:
        call_anthropic(
            client,
            system="s",
            user_message="u",
            model="claude-fable-5",
            max_tokens=64,
        )
    assert excinfo.value.category == "harmful_content"
    assert excinfo.value.explanation == "no"
    # Exactly one attempt: a refusal is a verdict, not transport noise.
    assert client.beta.messages.create.call_count == 1


def test_non_fable_refusal_stop_reason_not_checked() -> None:
    """Pre-tier behavior preserved for sonnet/haiku paths."""
    client = MagicMock()
    client.messages.create.return_value = _response("text", stop_reason="refusal")
    assert (
        call_anthropic(
            client,
            system="s",
            user_message="u",
            model="claude-sonnet-5",
            max_tokens=64,
        )
        == "text"
    )


def test_fable_400_carries_retention_hint() -> None:
    class _Fake400(Exception):
        status_code = 400

    client = MagicMock()
    client.beta.messages.create.side_effect = _Fake400("invalid_request_error: nope")
    with pytest.raises(AnthropicCallError) as excinfo:
        call_anthropic(
            client,
            system="s",
            user_message="u",
            model="claude-fable-5",
            max_tokens=64,
        )
    assert "30-day org data retention" in str(excinfo.value)
    assert "invalid_request_error: nope" in str(excinfo.value)


def test_non_fable_400_has_no_retention_hint() -> None:
    class _Fake400(Exception):
        status_code = 400

    client = MagicMock()
    client.messages.create.side_effect = _Fake400("bad payload")
    with pytest.raises(AnthropicCallError) as excinfo:
        call_anthropic(
            client,
            system="s",
            user_message="u",
            model="claude-sonnet-5",
            max_tokens=64,
        )
    assert "retention" not in str(excinfo.value)
