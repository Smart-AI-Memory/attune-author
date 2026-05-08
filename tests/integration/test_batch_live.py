"""Live integration test for the Anthropic Message Batches API.

Default-skipped. To run:

    ANTHROPIC_API_KEY=sk-ant-... RUN_LIVE_BATCH=1 \\
        pytest tests/integration/test_batch_live.py -m live

Costs ~$0.02 per run (two batched polish calls). Asserts:

- ``submit_batch`` returns a real batch id.
- ``poll_batch`` reaches ``ended`` (or marks as ``timed_out`` if
  Anthropic is slow today).
- Each result has either non-empty text or a structured error.

Tags ``@pytest.mark.live`` so projects that allow some live tests
in CI can opt in selectively.
"""

from __future__ import annotations

import os

import pytest

from attune_author.doc_gen._anthropic_batch import (
    BatchPolishRequest,
    poll_batch,
    submit_batch,
)

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(
        not os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("RUN_LIVE_BATCH") != "1",
        reason="Requires ANTHROPIC_API_KEY and RUN_LIVE_BATCH=1.",
    ),
]


def _request(custom_id: str, query: str) -> BatchPolishRequest:
    """Tiny prompt so the live call is cheap.

    System prompt is short on purpose — keeps token cost minimal
    and exercises the wire format without polishing real content.
    """
    return BatchPolishRequest(
        custom_id=custom_id,
        feature="test",
        depth="concept",
        system="Reply with a one-word sentence answering the user.",
        user_message=query,
        model="claude-haiku-4-5-20251001",
        max_tokens=64,
        cache_system=False,
    )


def test_submit_then_poll_two_request_batch() -> None:
    requests = [
        _request("req1", "What color is the sky? Answer in one word."),
        _request("req2", "What color is grass? Answer in one word."),
    ]

    batch_id = submit_batch(requests)
    assert batch_id.startswith("msgbatch_")

    final_status, results = poll_batch(
        batch_id,
        requests,
        # Live batch latency is hard to predict; give it 5 minutes.
        timeout_secs=300.0,
        poll_interval_secs=10.0,
    )

    assert final_status in {"ended", "timed_out"}
    assert len(results) == 2
    if final_status == "ended":
        # Each request should have either text or a structured error,
        # never both, never neither.
        for r in results:
            assert (r.text is None) ^ (r.error is None)
