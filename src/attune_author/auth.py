"""Subscription-first auth routing for attune-author LLM calls.

Phase 1 of the ``sibling-subscription-auth`` spec (attune-ai
``docs/specs/sibling-subscription-auth/``). When attune-author runs
under a Claude Code session (``CLAUDECODE=1``) and the
``claude-agent-sdk`` package is importable, single-turn LLM calls
route through the user's Claude subscription via
``claude_agent_sdk.query()`` — no ``ANTHROPIC_API_KEY`` required.
Otherwise calls fall back to the direct Anthropic SDK path in
:mod:`attune_author.doc_gen._anthropic`.

Mode resolution (first match wins):

1. Explicit ``auth_mode=`` argument (the CLI's ``--auth-mode``).
2. The ``ATTUNE_AUTHOR_AUTH_MODE`` environment variable.
3. ``auto`` — subscription when detectable, else API key.

The subscription path spawns a short-lived ``claude`` CLI
subprocess per call with ``setting_sources=[]`` so user/project
settings (SessionStart hooks, CLAUDE.md context injection) never
leak into the call or pollute its stream-json channel.

Scope note: only the *synchronous* polish path routes here. The
Anthropic Batches API paths (``--batch`` regen, maintenance batch)
have no subscription equivalent and always require
``ANTHROPIC_API_KEY``.
"""

from __future__ import annotations

import importlib.util
import logging
import os
from collections.abc import Callable

from attune_author.doc_gen._anthropic import AnthropicCallError, _redact

logger = logging.getLogger(__name__)

#: Environment variable that pins the auth mode for every call in
#: the process. The CLI's ``--auth-mode`` flag maps onto it.
AUTH_MODE_ENV = "ATTUNE_AUTHOR_AUTH_MODE"

VALID_AUTH_MODES = ("auto", "api", "sub")

_NO_CREDENTIALS_MESSAGE = (
    "No LLM credentials available. Either run inside a Claude Code "
    "session (subscription routing via claude-agent-sdk) or set "
    "ANTHROPIC_API_KEY for direct API access."
)


def _sdk_importable() -> bool:
    """Return True when ``claude_agent_sdk`` can be imported."""
    try:
        return importlib.util.find_spec("claude_agent_sdk") is not None
    except (ImportError, ValueError):
        return False


def subscription_available() -> bool:
    """Return True when subscription routing is possible right now.

    Requires both a detectable Claude Code session (the
    ``CLAUDECODE=1`` env var Claude Code sets in every subprocess
    it spawns) and an importable ``claude-agent-sdk``. A subscriber
    running from a plain terminal has neither and falls back to
    the API path — that's the expected, documented behavior.
    """
    return os.environ.get("CLAUDECODE") == "1" and _sdk_importable()


def api_key_available() -> bool:
    """Return True when a non-empty ``ANTHROPIC_API_KEY`` is set."""
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def _requested_mode(explicit: str | None) -> str:
    """Normalize the requested mode from explicit arg or env var."""
    mode = (explicit or os.environ.get(AUTH_MODE_ENV) or "auto").strip().lower()
    if mode not in VALID_AUTH_MODES:
        raise AnthropicCallError(
            f"Invalid auth mode {mode!r}; expected one of: " + ", ".join(VALID_AUTH_MODES)
        )
    return mode


def resolve_auth_mode(explicit: str | None = None) -> str:
    """Resolve the effective auth route: ``"sub"`` or ``"api"``.

    Args:
        explicit: Explicit mode override (``auto``/``api``/``sub``).
            When ``None``, the ``ATTUNE_AUTHOR_AUTH_MODE`` env var
            is consulted; when that's unset too, ``auto``.

    Returns:
        ``"sub"`` (subscription via the Agent SDK) or ``"api"``
        (direct Anthropic SDK).

    Raises:
        AnthropicCallError: If the mode string is invalid, or
            ``sub`` is forced while no subscription session is
            detectable.
    """
    mode = _requested_mode(explicit)
    if mode == "sub":
        if not subscription_available():
            raise AnthropicCallError(
                "auth mode 'sub' forced but no subscription session "
                "is detectable (CLAUDECODE is not set, or "
                "claude-agent-sdk is not installed)"
            )
        return "sub"
    if mode == "api":
        return "api"
    return "sub" if subscription_available() else "api"


def auth_telemetry() -> dict[str, float]:
    """Per-process counters of LLM calls by auth route.

    Stored on the function as an attribute so end-of-run summaries
    can read totals without module-level state — same idiom as
    ``generator._faithfulness_telemetry``. Reset via
    :func:`reset_auth_telemetry`.
    """
    state = getattr(auth_telemetry, "_state", None)
    if state is None:
        state = {"sub_calls": 0.0, "api_calls": 0.0}
        auth_telemetry._state = state  # type: ignore[attr-defined]
    return state


def reset_auth_telemetry() -> None:
    """Reset the per-process auth-route telemetry counters."""
    auth_telemetry._state = {  # type: ignore[attr-defined]
        "sub_calls": 0.0,
        "api_calls": 0.0,
    }


def auth_status() -> dict[str, object]:
    """Snapshot of the auth environment for diagnostics.

    Powers ``attune-author auth status``. Never raises: a forced
    ``sub`` mode that can't be satisfied is reported via the
    ``error`` key instead.

    Returns:
        Dict with the detection signals, the env-var override, the
        resolved route (or ``None`` on error), and ``error`` text.
    """
    try:
        resolved: str | None = resolve_auth_mode()
        error: str | None = None
    except AnthropicCallError as exc:
        resolved, error = None, str(exc)
    return {
        "claudecode": os.environ.get("CLAUDECODE") == "1",
        "sdk_importable": _sdk_importable(),
        "subscription_available": subscription_available(),
        "api_key_available": api_key_available(),
        "env_mode": os.environ.get(AUTH_MODE_ENV),
        "resolved_mode": resolved,
        "error": error,
    }


def call_llm(
    *,
    system: str,
    user_message: str,
    model: str,
    max_tokens: int,
    cache_system: bool = False,
    on_cache_usage: Callable[[int, int, str], None] | None = None,
    auth_mode: str | None = None,
) -> str:
    """Route a single-turn LLM call through subscription or API auth.

    Drop-in replacement for the ``get_client()`` +
    ``call_anthropic(...)`` pair: same prompt-facing arguments, but
    the credential decision happens here.

    In ``auto`` mode a failed subscription call falls back to the
    API path when ``ANTHROPIC_API_KEY`` is available (subscription
    expiry mid-run shouldn't kill a regen). A *forced* ``sub`` mode
    never falls back — the explicit override wins, including its
    failures.

    Args:
        system: System prompt.
        user_message: User-turn content.
        model: Anthropic model ID (used by both routes).
        max_tokens: Response token budget. API route only — the
            Agent SDK manages its own output budget.
        cache_system: Enable prompt caching of the system prompt.
            API route only; the subscription route's ``claude`` CLI
            applies prompt caching automatically.
        on_cache_usage: Cache-telemetry callback. API route only.
        auth_mode: Explicit mode override; see
            :func:`resolve_auth_mode`.

    Returns:
        The model's text response (may be empty).

    Raises:
        AnthropicCallError: On invalid mode, forced-mode credential
            mismatch, missing credentials, or call failure after
            the routing rules above are exhausted.
    """
    mode = resolve_auth_mode(auth_mode)
    if mode == "sub":
        forced_sub = _requested_mode(auth_mode) == "sub"
        try:
            text = _call_subscription(system=system, user_message=user_message, model=model)
        except Exception as exc:  # noqa: BLE001
            # INTENTIONAL: every subscription-path failure funnels
            # through one redaction + fallback decision point. The
            # redaction mirrors call_anthropic's contract; `from
            # None` keeps unredacted text out of __cause__.
            if forced_sub or not api_key_available():
                raise AnthropicCallError(_redact(str(exc))) from None
            logger.warning(
                "Subscription LLM call failed; falling back to the API key path: %s",
                _redact(str(exc)),
            )
        else:
            auth_telemetry()["sub_calls"] += 1
            return text

    from attune_author.doc_gen._anthropic import call_anthropic, get_client

    try:
        client = get_client()
    except AnthropicCallError:
        raise AnthropicCallError(_NO_CREDENTIALS_MESSAGE) from None
    text = call_anthropic(
        client,
        system=system,
        user_message=user_message,
        model=model,
        max_tokens=max_tokens,
        cache_system=cache_system,
        on_cache_usage=on_cache_usage,
    )
    auth_telemetry()["api_calls"] += 1
    return text


def _call_subscription(*, system: str, user_message: str, model: str) -> str:
    """Synchronous wrapper around the async Agent-SDK call.

    ``claude_agent_sdk.query()`` spawns a fresh ``claude`` CLI
    subprocess per call, so a per-call ``asyncio.run`` is safe here
    (no persistent client bound to a loop). When the calling thread
    already runs an event loop, the call is pushed to a worker
    thread instead.
    """
    import asyncio

    coro = _query_subscription(system=system, user_message=user_message, model=model)
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()


async def _query_subscription(*, system: str, user_message: str, model: str) -> str:
    """Single-turn completion via ``claude_agent_sdk.query()``.

    Collects ``AssistantMessage`` text blocks and prefers
    ``ResultMessage.result`` when present (it can be ``None`` on
    some runs — the assistant text is the fallback).
    """
    from claude_agent_sdk import (
        AssistantMessage,
        ClaudeAgentOptions,
        ResultMessage,
        TextBlock,
        query,
    )

    options = ClaudeAgentOptions(
        system_prompt=system,
        model=model,
        max_turns=1,
        tools=[],  # pure completion — no tool use
        setting_sources=[],  # no user/project settings (hooks, CLAUDE.md)
        env={"ATTUNE_AUTHOR_SDK_SUBPROCESS": "1"},
    )
    text_parts: list[str] = []
    result_text: str | None = None
    async for message in query(prompt=user_message, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    text_parts.append(block.text)
        elif isinstance(message, ResultMessage):
            if isinstance(message.result, str) and message.result.strip():
                result_text = message.result
    return result_text if result_text is not None else "".join(text_parts)
