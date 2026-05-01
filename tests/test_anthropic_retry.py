"""Tests for the retry/backoff logic in attune_author.doc_gen._anthropic.

Covers the three behaviors that ``call_anthropic`` is supposed
to guarantee:

1. Transient SDK errors (429, 529, ``APIConnectionError``) are
   retried up to ``_MAX_RETRIES`` with exponential backoff.
2. Non-retryable SDK errors raise immediately.
3. Credential material in exception text is redacted before
   the wrapped ``AnthropicCallError`` surfaces.

``time.sleep`` is patched in every test so the suite runs fast
and the backoff schedule is asserted via the mock's call args
rather than wall-clock time.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


def _api_status_error(status: int, message: str = "transient") -> Exception:
    """Build an anthropic.APIStatusError with the given status code.

    The real exception class needs a response object with a
    status_code; we hand it a MagicMock so the call_anthropic
    code path that reads ``exc.status_code`` works as it would
    against a live SDK error.
    """
    from anthropic import APIStatusError

    response = MagicMock()
    response.status_code = status
    response.headers = {}
    err = APIStatusError(message, response=response, body=None)
    # APIStatusError forwards .status_code from the response.
    return err


def _api_connection_error(message: str = "connection reset") -> Exception:
    from anthropic import APIConnectionError

    return APIConnectionError(request=MagicMock())


def _ok_response(text: str) -> MagicMock:
    block = MagicMock()
    block.text = text
    response = MagicMock()
    response.content = [block]
    return response


class TestRetryableErrors:
    """429 and 529 should be retried up to _MAX_RETRIES."""

    def test_retries_on_429_then_succeeds(self) -> None:
        from attune_author.doc_gen import _anthropic

        client = MagicMock()
        client.messages.create.side_effect = [
            _api_status_error(429),
            _ok_response("hello"),
        ]

        with patch.object(_anthropic.time, "sleep") as mock_sleep:
            result = _anthropic.call_anthropic(
                client,
                system="sys",
                user_message="hi",
                model="m",
                max_tokens=10,
            )

        assert result == "hello"
        assert client.messages.create.call_count == 2
        mock_sleep.assert_called_once_with(1.0)  # base delay on first retry

    def test_retries_on_529_overload(self) -> None:
        from attune_author.doc_gen import _anthropic

        client = MagicMock()
        client.messages.create.side_effect = [
            _api_status_error(529),
            _ok_response("ok"),
        ]

        with patch.object(_anthropic.time, "sleep"):
            result = _anthropic.call_anthropic(
                client, system="s", user_message="u", model="m", max_tokens=10
            )

        assert result == "ok"

    def test_retries_on_connection_error(self) -> None:
        from attune_author.doc_gen import _anthropic

        client = MagicMock()
        client.messages.create.side_effect = [
            _api_connection_error(),
            _ok_response("recovered"),
        ]

        with patch.object(_anthropic.time, "sleep"):
            result = _anthropic.call_anthropic(
                client, system="s", user_message="u", model="m", max_tokens=10
            )

        assert result == "recovered"

    def test_exponential_backoff_schedule(self) -> None:
        """Two retries should sleep 1s then 2s before the next attempt."""
        from attune_author.doc_gen import _anthropic

        client = MagicMock()
        client.messages.create.side_effect = [
            _api_status_error(429),
            _api_status_error(429),
            _ok_response("finally"),
        ]

        with patch.object(_anthropic.time, "sleep") as mock_sleep:
            result = _anthropic.call_anthropic(
                client, system="s", user_message="u", model="m", max_tokens=10
            )

        assert result == "finally"
        # Backoff: 1.0 * 2**0, then 1.0 * 2**1.
        assert [c.args[0] for c in mock_sleep.call_args_list] == [1.0, 2.0]

    def test_gives_up_after_max_retries(self) -> None:
        """Persistent 429s exhaust retries and raise AnthropicCallError."""
        from attune_author.doc_gen import _anthropic

        client = MagicMock()
        client.messages.create.side_effect = [
            _api_status_error(429, "rate limit hit"),
        ] * 4  # _MAX_RETRIES + 1 attempts

        with patch.object(_anthropic.time, "sleep"):
            with pytest.raises(_anthropic.AnthropicCallError):
                _anthropic.call_anthropic(
                    client,
                    system="s",
                    user_message="u",
                    model="m",
                    max_tokens=10,
                )

        # _MAX_RETRIES = 3 → 4 total attempts (1 initial + 3 retries).
        assert client.messages.create.call_count == 4


class TestNonRetryableErrors:
    """4xx that aren't 429, 5xx that aren't 529, and unknown
    exception types must raise immediately without retry.
    """

    def test_400_bad_request_raises_immediately(self) -> None:
        from attune_author.doc_gen import _anthropic

        client = MagicMock()
        client.messages.create.side_effect = _api_status_error(400, "bad input")

        with patch.object(_anthropic.time, "sleep") as mock_sleep:
            with pytest.raises(_anthropic.AnthropicCallError):
                _anthropic.call_anthropic(
                    client,
                    system="s",
                    user_message="u",
                    model="m",
                    max_tokens=10,
                )

        assert client.messages.create.call_count == 1
        mock_sleep.assert_not_called()

    def test_unknown_exception_raises_immediately(self) -> None:
        from attune_author.doc_gen import _anthropic

        client = MagicMock()
        client.messages.create.side_effect = ValueError("something else")

        with patch.object(_anthropic.time, "sleep") as mock_sleep:
            with pytest.raises(_anthropic.AnthropicCallError):
                _anthropic.call_anthropic(
                    client,
                    system="s",
                    user_message="u",
                    model="m",
                    max_tokens=10,
                )

        assert client.messages.create.call_count == 1
        mock_sleep.assert_not_called()


class TestCredentialRedaction:
    """Credential material in error text must be scrubbed."""

    def test_api_key_redacted_in_error_message(self) -> None:
        from attune_author.doc_gen import _anthropic

        client = MagicMock()
        # pragma: allowlist nextline secret
        leaky_msg = "auth failed for sk-ant-abc123def456ghi789jkl0"
        client.messages.create.side_effect = ValueError(leaky_msg)

        with pytest.raises(_anthropic.AnthropicCallError) as exc_info:
            _anthropic.call_anthropic(
                client, system="s", user_message="u", model="m", max_tokens=10
            )

        msg = str(exc_info.value)
        assert "sk-ant-abc123" not in msg
        assert "[REDACTED]" in msg

    def test_cause_chain_is_stripped(self) -> None:
        """``from None`` must scrub __cause__ so credentials can't
        leak through ``str(exc.__cause__)``.
        """
        from attune_author.doc_gen import _anthropic

        client = MagicMock()
        client.messages.create.side_effect = ValueError("boom")

        with pytest.raises(_anthropic.AnthropicCallError) as exc_info:
            _anthropic.call_anthropic(
                client, system="s", user_message="u", model="m", max_tokens=10
            )

        assert exc_info.value.__cause__ is None
