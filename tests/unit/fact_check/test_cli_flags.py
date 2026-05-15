"""Tests for ``--fact-check`` / ``--no-fact-check`` CLI flags.

The CLI flags translate to ``ATTUNE_AUTHOR_FACT_CHECK`` via
:func:`attune_author.cli._apply_fact_check_args`. The env var
is the single source of truth read by
:func:`attune_author.generator._run_fact_check`.

Per spec docs/specs/polish-fact-check/ task 1.9.
"""

from __future__ import annotations

import argparse

import pytest

from attune_author.cli import _apply_fact_check_args, _build_parser


@pytest.fixture
def fresh_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Clear ``ATTUNE_AUTHOR_FACT_CHECK`` so each test starts blank."""
    monkeypatch.delenv("ATTUNE_AUTHOR_FACT_CHECK", raising=False)


class TestFlagToEnvVar:
    def test_fact_check_strict_sets_env(self, fresh_env, monkeypatch):
        ns = argparse.Namespace(fact_check="strict", no_fact_check=False)
        _apply_fact_check_args(ns)
        assert __import__("os").environ.get("ATTUNE_AUTHOR_FACT_CHECK") == "strict"

    def test_fact_check_soft_sets_env(self, fresh_env, monkeypatch):
        ns = argparse.Namespace(fact_check="soft", no_fact_check=False)
        _apply_fact_check_args(ns)
        assert __import__("os").environ.get("ATTUNE_AUTHOR_FACT_CHECK") == "soft"

    def test_no_fact_check_sets_off(self, fresh_env, monkeypatch):
        ns = argparse.Namespace(fact_check=None, no_fact_check=True)
        _apply_fact_check_args(ns)
        assert __import__("os").environ.get("ATTUNE_AUTHOR_FACT_CHECK") == "off"

    def test_no_flag_leaves_env_unset(self, fresh_env):
        ns = argparse.Namespace(fact_check=None, no_fact_check=False)
        _apply_fact_check_args(ns)
        assert __import__("os").environ.get("ATTUNE_AUTHOR_FACT_CHECK") is None

    def test_existing_env_wins(self, monkeypatch):
        """Shell-level intent overrides the per-invocation flag."""
        monkeypatch.setenv("ATTUNE_AUTHOR_FACT_CHECK", "strict")
        ns = argparse.Namespace(fact_check="off", no_fact_check=False)
        _apply_fact_check_args(ns)
        # Strict (set in env) survives the "off" flag.
        assert __import__("os").environ.get("ATTUNE_AUTHOR_FACT_CHECK") == "strict"


class TestArgparseShape:
    def test_generate_accepts_fact_check_strict(self):
        parser = _build_parser()
        args = parser.parse_args(["generate", "foo", "--fact-check", "strict"])
        assert args.fact_check == "strict"
        assert args.no_fact_check is False

    def test_generate_accepts_no_fact_check(self):
        parser = _build_parser()
        args = parser.parse_args(["generate", "foo", "--no-fact-check"])
        assert args.no_fact_check is True
        assert args.fact_check is None

    def test_generate_rejects_mutex(self):
        parser = _build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(
                [
                    "generate",
                    "foo",
                    "--fact-check",
                    "soft",
                    "--no-fact-check",
                ]
            )

    def test_regenerate_accepts_fact_check(self):
        parser = _build_parser()
        args = parser.parse_args(["regenerate", "--fact-check", "off"])
        assert args.fact_check == "off"

    def test_fact_check_choices_are_validated(self):
        parser = _build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["generate", "foo", "--fact-check", "invalid"])
