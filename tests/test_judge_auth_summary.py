"""Tests for the judge auth-route summary annotation (task 2.5)."""

from __future__ import annotations

import logging
import sys
import types

import pytest

from attune_author.maintenance import _log_judge_auth_route_summary


def _install_fake_rag_auth(monkeypatch: pytest.MonkeyPatch, counters: dict) -> None:
    fake_auth = types.ModuleType("attune_rag.auth")
    fake_auth.auth_telemetry = lambda: counters  # type: ignore[attr-defined]
    fake_rag = types.ModuleType("attune_rag")
    fake_rag.auth = fake_auth  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "attune_rag", fake_rag)
    monkeypatch.setitem(sys.modules, "attune_rag.auth", fake_auth)


def test_logs_route_split_when_counters_present(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    _install_fake_rag_auth(monkeypatch, {"sub_calls": 3.0, "api_calls": 1.0})
    with caplog.at_level(logging.INFO, logger="attune_author.maintenance"):
        _log_judge_auth_route_summary()
    assert "3 call(s) subscription, 1 API" in caplog.text


def test_silent_when_no_judge_calls(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    _install_fake_rag_auth(monkeypatch, {"sub_calls": 0.0, "api_calls": 0.0})
    with caplog.at_level(logging.INFO, logger="attune_author.maintenance"):
        _log_judge_auth_route_summary()
    assert "subscription" not in caplog.text


def test_silent_when_attune_rag_lacks_auth_module(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    # attune-rag < 0.7 (or absent): the auth submodule import fails.
    monkeypatch.setitem(sys.modules, "attune_rag", None)
    monkeypatch.setitem(sys.modules, "attune_rag.auth", None)
    with caplog.at_level(logging.INFO, logger="attune_author.maintenance"):
        _log_judge_auth_route_summary()
    assert "subscription" not in caplog.text
