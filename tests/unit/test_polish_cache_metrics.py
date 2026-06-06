"""Tests for polish prompt-cache hit-rate telemetry.

Covers the spec ``polish-cache-hit-metrics``: capturing
``cache_creation_input_tokens`` / ``cache_read_input_tokens`` from
Anthropic responses, the ``PolishCacheStats`` hit-rate math, the
per-process accumulator, the end-of-run summary line, and the
low-hit-rate threshold warning.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from attune_author import polish
from attune_author.doc_gen import _anthropic
from attune_author.polish import (
    PolishCacheStats,
    format_polish_cache_summary,
    polish_cache_stats,
    reset_polish_cache_telemetry,
)


@pytest.fixture(autouse=True)
def _clean_telemetry():
    """Each test starts and ends with zeroed counters so the
    per-process accumulator can't leak across tests."""
    reset_polish_cache_telemetry()
    yield
    reset_polish_cache_telemetry()


# ---------------------------------------------------------------------------
# PolishCacheStats hit-rate math
# ---------------------------------------------------------------------------


class TestPolishCacheStats:
    def test_hit_rate_basic(self) -> None:
        stats = PolishCacheStats(calls=1, creation_tokens=180, read_tokens=1241)
        assert stats.total_tokens == 1421
        assert stats.hit_rate == pytest.approx(1241 / 1421)

    def test_hit_rate_full_hit(self) -> None:
        stats = PolishCacheStats(calls=2, creation_tokens=0, read_tokens=2048)
        assert stats.hit_rate == pytest.approx(1.0)

    def test_hit_rate_zero_tokens_is_safe(self) -> None:
        """No cacheable tokens must not divide by zero."""
        stats = PolishCacheStats(calls=1, creation_tokens=0, read_tokens=0)
        assert stats.total_tokens == 0
        assert stats.hit_rate == 0.0

    def test_summary_line_with_tokens(self) -> None:
        stats = PolishCacheStats(calls=3, creation_tokens=180, read_tokens=1241)
        line = stats.summary_line()
        assert "87%" in line  # 1241/1421 == 0.873...
        assert "1241 read" in line
        assert "1421 total" in line
        assert "3 call(s)" in line

    def test_summary_line_graceful_when_zero(self) -> None:
        stats = PolishCacheStats(calls=1, creation_tokens=0, read_tokens=0)
        assert "no cacheable tokens" in stats.summary_line().lower()


# ---------------------------------------------------------------------------
# call_anthropic on_cache_usage callback (the capture path)
# ---------------------------------------------------------------------------


def _mock_client(creation: int, read: int) -> MagicMock:
    client = MagicMock()
    block = MagicMock()
    block.text = "polished"
    response = MagicMock()
    response.content = [block]
    response.usage.cache_creation_input_tokens = creation
    response.usage.cache_read_input_tokens = read
    client.messages.create.return_value = response
    return client


class TestOnCacheUsageCallback:
    def test_callback_fires_with_token_counts(self) -> None:
        seen: list[tuple[int, int, str]] = []
        client = _mock_client(creation=1024, read=512)

        _anthropic.call_anthropic(
            client,
            system="s",
            user_message="u",
            model="claude-sonnet-4-6",
            max_tokens=10,
            on_cache_usage=lambda c, r, m: seen.append((c, r, m)),
        )

        assert seen == [(1024, 512, "claude-sonnet-4-6")]

    def test_callback_fires_even_when_zero(self) -> None:
        """Caller must be able to tell 'no cache' from 'never called'."""
        seen: list[tuple[int, int, str]] = []
        client = _mock_client(creation=0, read=0)

        _anthropic.call_anthropic(
            client,
            system="s",
            user_message="u",
            model="m",
            max_tokens=10,
            on_cache_usage=lambda c, r, m: seen.append((c, r, m)),
        )

        assert seen == [(0, 0, "m")]

    def test_no_callback_is_fine(self) -> None:
        """Omitting the callback (doc-gen path) must not error."""
        client = _mock_client(creation=10, read=10)
        out = _anthropic.call_anthropic(
            client, system="s", user_message="u", model="m", max_tokens=10
        )
        assert out == "polished"


# ---------------------------------------------------------------------------
# Accumulator + reset
# ---------------------------------------------------------------------------


class TestAccumulator:
    def test_records_accumulate_across_calls(self) -> None:
        polish._record_cache_usage(1000, 0, "m")  # creation-only (cold)
        polish._record_cache_usage(100, 900, "m")  # mostly read (warm)

        stats = polish_cache_stats()
        assert stats.calls == 2
        assert stats.creation_tokens == 1100
        assert stats.read_tokens == 900
        assert stats.total_tokens == 2000
        assert stats.hit_rate == pytest.approx(0.45)

    def test_reset_zeroes_counters(self) -> None:
        polish._record_cache_usage(100, 100, "m")
        reset_polish_cache_telemetry()
        stats = polish_cache_stats()
        assert (stats.calls, stats.creation_tokens, stats.read_tokens) == (0, 0, 0)


# ---------------------------------------------------------------------------
# End-of-run summary + threshold warning
# ---------------------------------------------------------------------------


class TestSummary:
    def test_summary_none_when_polish_never_ran(self) -> None:
        assert format_polish_cache_summary() is None

    def test_summary_present_after_calls(self) -> None:
        polish._record_cache_usage(180, 1241, "m")
        summary = format_polish_cache_summary()
        assert summary is not None
        assert "Polish cache hit" in summary
        assert "WARNING" not in summary  # 87% is healthy

    def test_low_hit_rate_appends_warning(self) -> None:
        # 100 read / 1000 total == 10% — below the 50% threshold.
        polish._record_cache_usage(900, 100, "m")
        summary = format_polish_cache_summary()
        assert summary is not None
        assert "WARNING" in summary
        assert "below 50%" in summary

    def test_zero_token_run_warns_nothing(self) -> None:
        """A run with calls but no cacheable tokens reports the
        graceful line and no spurious threshold warning."""
        polish._record_cache_usage(0, 0, "m")
        summary = format_polish_cache_summary()
        assert summary is not None
        assert "no cacheable tokens" in summary.lower()
        assert "WARNING" not in summary
