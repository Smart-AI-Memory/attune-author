"""Anthropic Message Batches API wrapper.

Mirrors :mod:`attune_author.doc_gen._anthropic`'s contract for
*N* prompts: build a single batch request, submit it, and poll
until the batch reaches a terminal state. Used by the
``attune-author maintain --batch`` flow as the cost-saving
alternative to per-call ``messages.create``.

The split across :func:`submit_batch` and :func:`poll_batch` is
deliberate — submit is a fast one-shot that the CLI uses on the
``--batch`` invocation, while polling happens later on
``--resume`` (potentially in a fresh process). They are
connected by the batch ID stored in the on-disk
``.help/.batch-state.json``.

Verified against ``anthropic`` SDK 0.89+:

- Resource path: ``client.messages.batches`` with
  ``create / cancel / retrieve / results``.
- :class:`anthropic.types.messages.MessageBatch` exposes
  ``processing_status``, ``request_counts``, ``expires_at``,
  ``cancel_initiated_at``, ``results_url``.
- :class:`MessageBatchIndividualResponse` carries
  ``custom_id`` + ``result`` (discriminated union of
  Succeeded / Errored / Expired / Canceled).
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from anthropic import Anthropic


# Status strings the SDK can return from ``processing_status``.
# We only branch on a small subset; the rest map to ``in_progress``.
_TERMINAL_STATUSES = {"ended", "canceled"}


@dataclass(frozen=True)
class BatchPolishRequest:
    """One polish request inside a batch.

    ``custom_id`` is the Anthropic-side per-request key. Callers
    set it to a stable string (we use ``feat__{feature}__{depth}``)
    so the resume splicer can map results back to (feature, depth)
    without consulting any other state.
    """

    custom_id: str
    feature: str
    depth: str
    system: str
    user_message: str
    model: str
    max_tokens: int
    cache_system: bool = False


@dataclass(frozen=True)
class BatchPolishResult:
    """One polish response from a batch.

    Exactly one of ``text`` / ``error`` is non-None. ``error``
    is a short string that mirrors today's per-call failure
    messages (e.g. ``"anthropic.RateLimitError: ..."``).
    Special sentinel values: ``"timed_out"`` (poll-loop ceiling
    exceeded), ``"expired"`` (batch hit Anthropic's 24h window),
    ``"canceled"`` (batch was canceled).
    """

    custom_id: str
    feature: str
    depth: str
    text: str | None
    error: str | None


def _build_request_param(req: BatchPolishRequest) -> dict[str, Any]:
    """Render one ``BatchPolishRequest`` as the SDK's per-request envelope.

    Anthropic batches wrap the same Messages payload we use
    today; the only difference is the per-entry ``custom_id``
    plus the ``params`` envelope. ``cache_control`` on the
    system prompt works the same as the synchronous path.
    """
    if req.cache_system:
        system_payload: object = [
            {
                "type": "text",
                "text": req.system,
                "cache_control": {"type": "ephemeral"},
            }
        ]
    else:
        system_payload = req.system

    return {
        "custom_id": req.custom_id,
        "params": {
            "model": req.model,
            "max_tokens": req.max_tokens,
            "system": system_payload,
            "messages": [{"role": "user", "content": req.user_message}],
        },
    }


def submit_batch(
    requests: list[BatchPolishRequest],
    *,
    client: Anthropic | None = None,
) -> str:
    """Post one Anthropic batch and return its ``batch_id``.

    Does not poll. Mirrors the synchronous-path pattern: caller
    supplies an explicit client (for tests) or we build one from
    ``ANTHROPIC_API_KEY`` via the shared helper.
    """
    if not requests:
        raise ValueError("submit_batch requires at least one request")

    if client is None:
        from ._anthropic import get_client

        client = get_client()

    payload = [_build_request_param(r) for r in requests]
    batch = client.messages.batches.create(requests=payload)
    return batch.id


def adaptive_timeout_secs(num_requests: int) -> float:
    """Default poll-loop ceiling, scaled to batch size.

    Empirical Anthropic batch latency is ~30s baseline plus
    linear growth. We give 5min minimum (handles cold-start
    variance) plus 1min per 20 requests, capped at 30min so
    a single ``--resume`` invocation can't burn an entire
    afternoon. Spec design.md "Adaptive polling and timeout (D2)".
    """
    return min(30 * 60, max(5 * 60, 60 * (num_requests / 20)))


def poll_batch(
    batch_id: str,
    expected_requests: list[BatchPolishRequest],
    *,
    client: Anthropic | None = None,
    poll_interval_secs: float = 30.0,
    timeout_secs: float | None = None,
    on_progress: Callable[[Any], None] | None = None,
    _now: Callable[[], float] = time.monotonic,
    _sleep: Callable[[float], None] = time.sleep,
) -> tuple[str, list[BatchPolishResult]]:
    """Poll until the batch reaches terminal state.

    Returns ``(final_status, results)``:

    - ``final_status`` ∈ ``{"ended", "canceled", "expired", "timed_out"}``.
    - ``results`` has one entry per ``expected_requests`` item, in
      the same order. On ``timed_out`` (poll-loop ceiling exceeded
      before Anthropic finished), missing entries become
      ``BatchPolishResult(error="timed_out")``.

    SIGINT raises :class:`KeyboardInterrupt` after attempting
    to cancel the batch — surviving completed work is reflected
    in the partial results returned by a follow-up
    ``poll_batch`` call.

    ``_now`` and ``_sleep`` are injection points for tests; do
    not pass them in production.
    """
    if client is None:
        from ._anthropic import get_client

        client = get_client()

    if timeout_secs is None:
        timeout_secs = adaptive_timeout_secs(len(expected_requests))

    started = _now()
    deadline = started + timeout_secs

    try:
        while True:
            batch = client.messages.batches.retrieve(batch_id)
            if on_progress is not None:
                on_progress(batch)

            status = getattr(batch, "processing_status", "in_progress") or "in_progress"
            if status in _TERMINAL_STATUSES:
                results = _collect_results(client, batch_id, expected_requests)
                final_status = _final_status_from_terminal(batch, status)
                return final_status, results

            if _now() >= deadline:
                # Best-effort: pull any results Anthropic has produced so far.
                # Some batches expose partial results before they're terminal,
                # so we attempt a fetch but tolerate failure.
                partial = _collect_partial_results(client, batch_id, expected_requests)
                return "timed_out", partial

            _sleep(poll_interval_secs)
    except KeyboardInterrupt:
        # Best-effort cancel so the user isn't billed for new work
        # after they hit Ctrl+C. SIGINT propagates so the CLI can
        # clean up the state file and print a clear message.
        try:
            client.messages.batches.cancel(batch_id)
        except Exception:  # noqa: BLE001 — cancel is best-effort
            pass
        raise


def _final_status_from_terminal(batch: Any, status: str) -> str:
    """Translate the SDK's terminal ``processing_status`` to our taxonomy.

    ``ended`` is the success path; we further check
    ``request_counts`` and the presence of ``cancel_initiated_at``
    or expired-result rows to surface ``canceled`` vs
    ``expired`` as appropriate.
    """
    if status == "canceled":
        return "canceled"
    if getattr(batch, "cancel_initiated_at", None):
        return "canceled"
    counts = getattr(batch, "request_counts", None)
    if counts is not None and getattr(counts, "expired", 0) > 0:
        return "expired"
    return "ended"


def _collect_results(
    client: Anthropic,
    batch_id: str,
    expected: list[BatchPolishRequest],
) -> list[BatchPolishResult]:
    """Fetch and parse all per-request results.

    The SDK's ``results()`` returns an iterator of
    :class:`MessageBatchIndividualResponse`. We map each by
    ``custom_id`` then walk ``expected`` to produce a
    same-order list — keeps splicing on the orchestration side
    O(N) and order-deterministic for tests.
    """
    by_id: dict[str, Any] = {}
    for entry in client.messages.batches.results(batch_id):
        cid = getattr(entry, "custom_id", None)
        if cid:
            by_id[cid] = entry

    out: list[BatchPolishResult] = []
    for req in expected:
        entry = by_id.get(req.custom_id)
        if entry is None:
            out.append(_missing_result(req, "missing_in_results"))
            continue
        out.append(_parse_individual(entry, req))
    return out


def _collect_partial_results(
    client: Anthropic,
    batch_id: str,
    expected: list[BatchPolishRequest],
) -> list[BatchPolishResult]:
    """Try to fetch results for a non-terminal batch (timeout path).

    Most batches won't expose results until terminal, but the
    SDK doesn't refuse the call. Any request with no result
    becomes ``error="timed_out"`` so the caller's failure
    surface is filled.
    """
    try:
        results = _collect_results(client, batch_id, expected)
    except Exception:  # noqa: BLE001 — partial-fetch is best-effort
        results = [_missing_result(r, "timed_out") for r in expected]
        return results

    timed_out: list[BatchPolishResult] = []
    for req, res in zip(expected, results, strict=True):
        if res.error == "missing_in_results":
            timed_out.append(_missing_result(req, "timed_out"))
        else:
            timed_out.append(res)
    return timed_out


def _missing_result(req: BatchPolishRequest, error: str) -> BatchPolishResult:
    return BatchPolishResult(
        custom_id=req.custom_id,
        feature=req.feature,
        depth=req.depth,
        text=None,
        error=error,
    )


def _parse_individual(entry: Any, req: BatchPolishRequest) -> BatchPolishResult:
    """Parse one ``MessageBatchIndividualResponse`` into our type.

    The ``result`` field is a discriminated union; we branch on
    its ``type`` and pull either the response text (succeeded)
    or a short error string (everything else).
    """
    result = getattr(entry, "result", None)
    rtype = getattr(result, "type", None)

    if rtype == "succeeded":
        message = getattr(result, "message", None)
        text = _first_text_block(message)
        return BatchPolishResult(
            custom_id=req.custom_id,
            feature=req.feature,
            depth=req.depth,
            text=text,
            error=None,
        )

    if rtype == "errored":
        err = getattr(result, "error", None)
        # SDK shape: result.error.error.{type, message} or similar.
        # Walk defensively so unfamiliar shapes don't crash.
        message = (
            _resolve_attr(err, "message")
            or _resolve_attr(err, "error", "message")
            or "unknown error"
        )
        return BatchPolishResult(
            custom_id=req.custom_id,
            feature=req.feature,
            depth=req.depth,
            text=None,
            error=str(message),
        )

    if rtype in {"expired", "canceled"}:
        return BatchPolishResult(
            custom_id=req.custom_id,
            feature=req.feature,
            depth=req.depth,
            text=None,
            error=rtype,
        )

    # Unknown or missing result type — defensive default.
    return BatchPolishResult(
        custom_id=req.custom_id,
        feature=req.feature,
        depth=req.depth,
        text=None,
        error=f"unknown_result_type:{rtype}",
    )


def _first_text_block(message: Any) -> str:
    """Return the first text block from a message-shaped object."""
    if message is None:
        return ""
    content = getattr(message, "content", None) or []
    for block in content:
        text = getattr(block, "text", None)
        if text:
            return text
    return ""


def _resolve_attr(obj: Any, *path: str) -> Any:
    """Walk ``path`` of attributes; return None on any miss."""
    cur = obj
    for name in path:
        if cur is None:
            return None
        cur = getattr(cur, name, None)
    return cur
