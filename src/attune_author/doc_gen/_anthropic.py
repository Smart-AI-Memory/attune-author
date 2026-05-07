"""Shared Anthropic API call helper.

Centralizes client construction, ``messages.create`` invocation,
and error-surface hygiene for every code path that talks to the
Anthropic SDK (the three doc-gen stages and the polish pass).
Keeping one chokepoint means the redaction rule below applies
uniformly — API keys can't leak through a forgotten callsite.
"""

from __future__ import annotations

import logging
import os
import re
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from anthropic import Anthropic

logger = logging.getLogger(__name__)

_MAX_RETRIES = 3
_RETRY_BASE_DELAY = 1.0  # seconds; doubles each attempt

#: Source-content character budgets per doc-gen stage. Tuned so
#: the outline and review stages see enough code for accuracy
#: without dominating the prompt context, while the write stage
#: gets the largest window for grounded examples.
OUTLINE_SOURCE_CHARS = 4000
WRITE_SOURCE_CHARS = 5000
REVIEW_SOURCE_CHARS = 3000

# Patterns that could carry credentials through exception text.
_KEY_PATTERN = re.compile(r"sk-ant-[A-Za-z0-9_\-]{10,}")
_REDACTED = "sk-ant-[REDACTED]"


class AnthropicCallError(RuntimeError):
    """Raised when an Anthropic SDK call fails.

    The message is always the redacted form of the original
    exception text. The original SDK exception is not chained
    (``from None``) so that callers inspecting ``__cause__``
    can't accidentally surface an unredacted message.
    """


def _redact(text: str) -> str:
    """Remove anything that looks like an Anthropic API key.

    Args:
        text: Raw string that may contain credential material.

    Returns:
        ``text`` with every ``sk-ant-...`` token replaced by a
        fixed placeholder.
    """
    return _KEY_PATTERN.sub(_REDACTED, text)


def _is_retryable(exc: Exception) -> bool:
    """Return True for transient Anthropic errors that are safe to retry."""
    try:
        from anthropic import APIConnectionError, APIStatusError
    except ImportError:
        return False
    if isinstance(exc, APIConnectionError):
        return True
    if isinstance(exc, APIStatusError):
        return exc.status_code in (429, 529)
    return False


def get_client(api_key: str | None = None) -> Anthropic:
    """Instantiate an Anthropic client.

    Args:
        api_key: Explicit key. When ``None``, reads
            ``ANTHROPIC_API_KEY`` from the environment.

    Returns:
        An instantiated ``Anthropic`` client.

    Raises:
        AnthropicCallError: If no API key is available. Using
            a single error type lets callers catch one thing.
    """
    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise AnthropicCallError("ANTHROPIC_API_KEY not set")
    from anthropic import Anthropic

    return Anthropic(api_key=key)


def call_anthropic(
    client: Anthropic,
    *,
    system: str,
    user_message: str,
    model: str,
    max_tokens: int,
    cache_system: bool = False,
) -> str:
    """Make a single-turn ``messages.create`` call with retry/backoff.

    Retries up to ``_MAX_RETRIES`` times on transient errors (rate
    limits and overload responses). Non-transient SDK errors fail
    immediately. All exceptions are re-raised as
    :class:`AnthropicCallError` with a redacted message and an
    empty ``__cause__`` chain to guarantee credential material
    cannot leak through ``str(exc.__cause__)``.

    Args:
        client: Instantiated Anthropic client.
        system: System prompt.
        user_message: User-turn content.
        model: Anthropic model ID.
        max_tokens: Response token budget.
        cache_system: When True, wraps ``system`` as a content-block
            list with an ``ephemeral`` ``cache_control`` marker.
            Anthropic's prompt caching kicks in when the cacheable
            block crosses a model-specific threshold (1024 tokens
            for sonnet/opus, 2048 for haiku); below that, the call
            still works but no cache is used. Cache token usage is
            emitted at INFO so callers can verify hits.

    Returns:
        The first text block of the response, or the empty
        string if the response carried no content.

    Raises:
        AnthropicCallError: On any SDK or transport failure after
            retries are exhausted.
    """
    if cache_system:
        system_payload: object = [
            {
                "type": "text",
                "text": system,
                "cache_control": {"type": "ephemeral"},
            }
        ]
    else:
        system_payload = system

    last_exc: Exception | None = None
    for attempt in range(_MAX_RETRIES + 1):
        if attempt:
            delay = _RETRY_BASE_DELAY * (2 ** (attempt - 1))
            logger.warning(
                "Anthropic call failed (attempt %d/%d), retrying in %.1fs: %s",
                attempt,
                _MAX_RETRIES,
                delay,
                _redact(str(last_exc)),
            )
            time.sleep(delay)
        try:
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system_payload,
                messages=[{"role": "user", "content": user_message}],
            )
            _log_cache_usage(response, model)
            if response.content:
                return response.content[0].text
            return ""
        except Exception as exc:  # noqa: BLE001
            # INTENTIONAL: every SDK exception type funnels through
            # one redaction pass so credential material can't leak
            # into logs, error surfaces, or upstream exception
            # chains. `from None` strips __cause__ so callers
            # inspecting the chain only ever see the redacted form.
            if _is_retryable(exc):
                last_exc = exc
                continue
            raise AnthropicCallError(_redact(str(exc))) from None

    raise AnthropicCallError(_redact(str(last_exc))) from None


def _log_cache_usage(response: object, model: str) -> None:
    """Emit cache hit telemetry from an Anthropic response.

    Reads ``cache_creation_input_tokens`` and ``cache_read_input_tokens``
    from the response's usage object when present and logs them at INFO.
    Older SDK responses without those fields are silently skipped.
    """
    usage = getattr(response, "usage", None)
    if usage is None:
        return
    creation = getattr(usage, "cache_creation_input_tokens", 0) or 0
    read = getattr(usage, "cache_read_input_tokens", 0) or 0
    if creation or read:
        logger.info(
            "anthropic cache: model=%s creation=%d read=%d",
            model,
            creation,
            read,
        )
