"""Unit tests for the Anthropic Message Batches API wrapper.

Three surfaces covered:

1. **Payload shape** — :func:`_build_request_param` produces the
   exact wire format the SDK expects, including the
   ``cache_control`` wrap when ``cache_system=True``.
2. **Submit** — :func:`submit_batch` posts the rendered payload
   and returns the batch id from the SDK response.
3. **Poll loop** — :func:`poll_batch` covers the full state
   matrix: in_progress→ended, ended-with-errors, canceled,
   timed_out, ctrl-c-during-poll. All driven by a stub SDK; no
   live calls.

The recorded fixture lives at ``tests/golden/batch_response.json``
and mirrors the SDK's ``MessageBatch`` + ``MessageBatchIndividual
Response`` shape.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from attune_author.doc_gen._anthropic_batch import (
    BatchPolishRequest,
    BatchPolishResult,
    _build_request_param,
    adaptive_timeout_secs,
    poll_batch,
    submit_batch,
)

_FIXTURE = Path(__file__).resolve().parent / "golden" / "batch_response.json"


def _req(
    custom_id: str,
    feature: str = "f",
    depth: str = "concept",
    *,
    cache_system: bool = False,
) -> BatchPolishRequest:
    return BatchPolishRequest(
        custom_id=custom_id,
        feature=feature,
        depth=depth,
        system="sys-prompt",
        user_message="user-msg",
        model="claude-sonnet-4-6",
        max_tokens=2048,
        cache_system=cache_system,
    )


def _ns(**kwargs: object) -> SimpleNamespace:
    return SimpleNamespace(**kwargs)


def _fixture_results() -> list[SimpleNamespace]:
    """Translate the fixture's ``_results`` array into SimpleNamespaces.

    Mirrors the runtime shape: each entry has ``custom_id`` and
    ``result``; ``result`` carries ``type`` plus a discriminated
    payload. The same recursive walk would work for any future
    SDK shape change.
    """
    raw = json.loads(_FIXTURE.read_text())
    out: list[SimpleNamespace] = []
    for entry in raw["_results"]:
        result_dict = entry["result"]
        rtype = result_dict["type"]
        if rtype == "succeeded":
            msg_dict = result_dict["message"]
            content = [_ns(**block) for block in msg_dict.get("content", [])]
            message = _ns(content=content, **{k: v for k, v in msg_dict.items() if k != "content"})
            result = _ns(type=rtype, message=message)
        elif rtype == "errored":
            err_outer = result_dict["error"]
            inner = err_outer.get("error", {}) or {}
            error = _ns(
                type=err_outer.get("type"),
                error=_ns(**inner),
                message=inner.get("message"),
            )
            result = _ns(type=rtype, error=error)
        else:
            result = _ns(type=rtype)
        out.append(_ns(custom_id=entry["custom_id"], result=result))
    return out


def _fixture_batch(processing_status: str = "ended") -> SimpleNamespace:
    raw = json.loads(_FIXTURE.read_text())
    return _ns(
        id=raw["id"],
        processing_status=processing_status,
        request_counts=_ns(**raw["request_counts"]),
        ended_at=raw["ended_at"],
        expires_at=raw["expires_at"],
        created_at=raw["created_at"],
        cancel_initiated_at=raw["cancel_initiated_at"],
        results_url=raw["results_url"],
    )


def _stub_client(
    *,
    batch_states: list[SimpleNamespace] | None = None,
    results: list[SimpleNamespace] | None = None,
    create_id: str = "msgbatch_01abc123",
) -> MagicMock:
    """Build a stub SDK client.

    ``batch_states`` is the sequence ``retrieve`` returns on
    successive calls (so a poll loop can transition through
    in_progress → ended). ``results`` is the list ``results()``
    yields on terminal state.
    """
    client = MagicMock()
    client.messages.batches.create.return_value = _ns(id=create_id)
    if batch_states:
        client.messages.batches.retrieve.side_effect = batch_states
    if results is not None:
        client.messages.batches.results.return_value = iter(results)
    return client


# --- payload shape ----------------------------------------------------------


def test_build_request_param_default_no_cache() -> None:
    p = _build_request_param(_req("feat__a__concept"))
    assert p["custom_id"] == "feat__a__concept"
    assert p["params"]["model"] == "claude-sonnet-4-6"
    assert p["params"]["max_tokens"] == 2048
    assert p["params"]["system"] == "sys-prompt"
    assert p["params"]["messages"] == [{"role": "user", "content": "user-msg"}]


def test_build_request_param_with_cache_wraps_system_block() -> None:
    p = _build_request_param(_req("feat__a__concept", cache_system=True))
    assert p["params"]["system"] == [
        {
            "type": "text",
            "text": "sys-prompt",
            "cache_control": {"type": "ephemeral"},
        }
    ]


# --- submit -----------------------------------------------------------------


def test_submit_batch_rejects_empty_requests() -> None:
    with pytest.raises(ValueError, match="at least one request"):
        submit_batch([], client=MagicMock())


def test_submit_batch_renders_payload_and_returns_id() -> None:
    client = _stub_client(create_id="msgbatch_xyz")
    batch_id = submit_batch(
        [
            _req("feat__a__concept", feature="a"),
            _req("feat__b__task", feature="b", depth="task"),
        ],
        client=client,
    )
    assert batch_id == "msgbatch_xyz"
    sent = client.messages.batches.create.call_args.kwargs["requests"]
    assert len(sent) == 2
    assert sent[0]["custom_id"] == "feat__a__concept"
    assert sent[1]["custom_id"] == "feat__b__task"


# --- poll loop --------------------------------------------------------------


def test_poll_terminal_ended_with_results_splices_in_input_order() -> None:
    """The order of ``BatchPolishResult`` matches the order of the
    ``expected`` argument, regardless of what order Anthropic
    returns results in.
    """
    expected = [
        _req("feat__security-audit__concept", feature="security-audit"),
        _req("feat__security-audit__task", feature="security-audit", depth="task"),
        _req("feat__smart-test__concept", feature="smart-test"),
    ]
    client = _stub_client(
        batch_states=[_fixture_batch("ended")],
        results=list(reversed(_fixture_results())),  # out-of-order on the wire
    )
    status, results = poll_batch(
        "msgbatch_01abc123",
        expected,
        client=client,
        _now=lambda: 0.0,
        _sleep=lambda _: None,
    )
    assert status == "ended"
    assert [r.custom_id for r in results] == [r.custom_id for r in expected]
    assert results[0].text == "Polished concept template body for security-audit."
    assert results[1].text == "Polished task template body for security-audit."
    assert results[2].text is None
    assert "Rate limit" in (results[2].error or "")


def test_poll_in_progress_then_ended_advances_through_states() -> None:
    expected = [_req("feat__a__concept", feature="a")]
    in_progress = _fixture_batch("in_progress")
    in_progress.request_counts = _ns(canceled=0, errored=0, expired=0, processing=1, succeeded=0)
    ended = _fixture_batch("ended")
    ended.request_counts = _ns(canceled=0, errored=0, expired=0, processing=0, succeeded=1)
    client = _stub_client(
        batch_states=[in_progress, ended],
        results=[_fixture_results()[0]],
    )
    sleeps: list[float] = []
    status, results = poll_batch(
        "msgbatch_01abc123",
        expected,
        client=client,
        poll_interval_secs=12.5,
        _now=lambda: 0.0,
        _sleep=sleeps.append,
    )
    assert status == "ended"
    assert sleeps == [12.5]  # exactly one sleep between two poll cycles
    assert client.messages.batches.retrieve.call_count == 2


def test_poll_canceled_status_returns_canceled() -> None:
    expected = [_req("feat__a__concept", feature="a")]
    canceled = _fixture_batch("canceled")
    client = _stub_client(batch_states=[canceled], results=[])
    status, _ = poll_batch(
        "msgbatch_01abc123",
        expected,
        client=client,
        _now=lambda: 0.0,
        _sleep=lambda _: None,
    )
    assert status == "canceled"


def test_poll_cancel_initiated_treated_as_canceled() -> None:
    """Even with processing_status='ended', a non-null
    cancel_initiated_at means the user canceled mid-flight."""
    expected = [_req("feat__a__concept", feature="a")]
    batch = _fixture_batch("ended")
    batch.cancel_initiated_at = "2026-05-08T18:40:00Z"
    client = _stub_client(batch_states=[batch], results=_fixture_results()[:1])
    status, _ = poll_batch(
        "msgbatch_01abc123",
        expected,
        client=client,
        _now=lambda: 0.0,
        _sleep=lambda _: None,
    )
    assert status == "canceled"


def test_poll_expired_count_surfaces_expired_status() -> None:
    expected = [_req("feat__a__concept", feature="a")]
    batch = _fixture_batch("ended")
    batch.request_counts = _ns(canceled=0, errored=0, expired=1, processing=0, succeeded=0)
    client = _stub_client(batch_states=[batch], results=[])
    status, _ = poll_batch(
        "msgbatch_01abc123",
        expected,
        client=client,
        _now=lambda: 0.0,
        _sleep=lambda _: None,
    )
    assert status == "expired"


def test_poll_timeout_returns_timed_out_with_unfinished_marked() -> None:
    """When the poll-loop ceiling fires before the batch is
    terminal, every unfinished entry surfaces as
    ``error="timed_out"`` so the orchestration layer can mark
    them in ``MaintenanceResult.failed``.
    """
    expected = [
        _req("feat__a__concept", feature="a"),
        _req("feat__b__concept", feature="b"),
    ]
    in_progress = _fixture_batch("in_progress")
    client = _stub_client(batch_states=[in_progress, in_progress, in_progress], results=[])
    ticks = iter([0.0, 100.0, 200.0])
    status, results = poll_batch(
        "msgbatch_01abc123",
        expected,
        client=client,
        timeout_secs=50.0,
        poll_interval_secs=10.0,
        _now=lambda: next(ticks),
        _sleep=lambda _: None,
    )
    assert status == "timed_out"
    assert all(r.text is None and r.error == "timed_out" for r in results)
    assert [r.custom_id for r in results] == [r.custom_id for r in expected]


def test_poll_ctrl_c_cancels_batch_and_re_raises() -> None:
    """SIGINT mid-poll calls cancel and re-raises so the CLI can
    clean up its state file. Cancel failures must not mask the
    KeyboardInterrupt."""
    expected = [_req("feat__a__concept", feature="a")]
    client = MagicMock()
    client.messages.batches.retrieve.side_effect = KeyboardInterrupt
    with pytest.raises(KeyboardInterrupt):
        poll_batch(
            "msgbatch_01abc123",
            expected,
            client=client,
            _now=lambda: 0.0,
            _sleep=lambda _: None,
        )
    client.messages.batches.cancel.assert_called_once_with("msgbatch_01abc123")


def test_poll_ctrl_c_cancel_failure_does_not_mask_interrupt() -> None:
    expected = [_req("feat__a__concept", feature="a")]
    client = MagicMock()
    client.messages.batches.retrieve.side_effect = KeyboardInterrupt
    client.messages.batches.cancel.side_effect = RuntimeError("network down")
    with pytest.raises(KeyboardInterrupt):
        poll_batch(
            "msgbatch_01abc123",
            expected,
            client=client,
            _now=lambda: 0.0,
            _sleep=lambda _: None,
        )


def test_poll_missing_result_for_request_marks_missing() -> None:
    """If results() returns an entry for an unknown custom_id (or
    omits one), the affected request becomes
    ``error="missing_in_results"`` rather than crashing."""
    expected = [
        _req("feat__security-audit__concept", feature="security-audit"),
        _req("feat__missing__concept", feature="missing"),
    ]
    client = _stub_client(
        batch_states=[_fixture_batch("ended")],
        results=[_fixture_results()[0]],  # only the security-audit entry
    )
    _, results = poll_batch(
        "msgbatch_01abc123",
        expected,
        client=client,
        _now=lambda: 0.0,
        _sleep=lambda _: None,
    )
    assert results[0].text is not None
    assert results[1].text is None
    assert results[1].error == "missing_in_results"


def test_poll_progress_callback_invoked_each_retrieve() -> None:
    expected = [_req("feat__a__concept", feature="a")]
    client = _stub_client(
        batch_states=[_fixture_batch("ended")],
        results=[_fixture_results()[0]],
    )
    seen: list[object] = []
    poll_batch(
        "msgbatch_01abc123",
        expected,
        client=client,
        on_progress=seen.append,
        _now=lambda: 0.0,
        _sleep=lambda _: None,
    )
    assert len(seen) == 1


def test_poll_unknown_result_type_does_not_crash() -> None:
    expected = [_req("feat__sample__concept", feature="sample")]
    client = _stub_client(
        batch_states=[_fixture_batch("ended")],
        results=[
            _ns(
                custom_id="feat__sample__concept",
                result=_ns(type="some_future_status"),
            )
        ],
    )
    status, results = poll_batch(
        "msgbatch_01abc123",
        expected,
        client=client,
        _now=lambda: 0.0,
        _sleep=lambda _: None,
    )
    assert status == "ended"
    assert results[0].error == "unknown_result_type:some_future_status"


# --- adaptive_timeout_secs --------------------------------------------------


def test_adaptive_timeout_floor_for_small_batches() -> None:
    assert adaptive_timeout_secs(0) == 5 * 60
    assert adaptive_timeout_secs(1) == 5 * 60
    assert adaptive_timeout_secs(50) == 5 * 60


def test_adaptive_timeout_grows_linearly_above_floor() -> None:
    assert adaptive_timeout_secs(200) == pytest.approx(600.0)


def test_adaptive_timeout_capped_at_30_minutes() -> None:
    assert adaptive_timeout_secs(10_000) == 30 * 60


# --- BatchPolishResult contract --------------------------------------------


def test_batch_polish_result_text_xor_error_invariant() -> None:
    """Construction can produce either successful (text set, error
    None) or failed (text None, error set) results — but the
    parser layer never produces both, so this contract gives
    downstream consumers a clean discriminator."""
    ok = BatchPolishResult(custom_id="x", feature="f", depth="d", text="hello", error=None)
    bad = BatchPolishResult(custom_id="x", feature="f", depth="d", text=None, error="boom")
    assert (ok.text is None) ^ (ok.error is None)
    assert (bad.text is None) ^ (bad.error is None)
