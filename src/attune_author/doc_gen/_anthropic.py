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
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from anthropic import Anthropic

logger = logging.getLogger(__name__)

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
) -> str:
    """Make a single-turn ``messages.create`` call.

    Wraps the SDK call so every caller shares identical error
    handling, message shape, and response unwrapping. Any
    exception raised by the SDK is re-raised as
    :class:`AnthropicCallError` with a redacted message and an
    empty ``__cause__`` chain to guarantee credential material
    cannot leak through ``str(exc.__cause__)``.

    Args:
        client: Instantiated Anthropic client.
        system: System prompt.
        user_message: User-turn content.
        model: Anthropic model ID.
        max_tokens: Response token budget.

    Returns:
        The first text block of the response, or the empty
        string if the response carried no content.

    Raises:
        AnthropicCallError: On any SDK or transport failure.
    """
    try:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user_message}],
        )
    except Exception as exc:  # noqa: BLE001
        # INTENTIONAL: every SDK exception type funnels through
        # one redaction pass so credential material can't leak
        # into logs, error surfaces, or upstream exception
        # chains. `from None` strips __cause__ so callers
        # inspecting the chain only ever see the redacted form.
        raise AnthropicCallError(_redact(str(exc))) from None

    if response.content:
        return response.content[0].text
    return ""
