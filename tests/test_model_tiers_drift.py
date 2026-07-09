"""Drift guard: attune_author.model_tiers must mirror attune_rag.model_tiers.

The tier module is duplicated by design (attune-rag is only an optional
``[rag]`` extra here — see specs/fable-model-tiers design in the attune
workspace repo). Duplication is acceptable only with an automated drift
alarm — the lesson from the sibling-hooks drift problem. This test IS
that alarm: it fails the moment the two copies' contract constants
diverge.

Skips (not fails) when the installed attune-rag predates model_tiers or
the ``[rag]`` extra is absent locally; CI installs ``[rag]`` at a
model_tiers-carrying version, so drift cannot ship unnoticed.
"""

from __future__ import annotations

import pytest

rag_tiers = pytest.importorskip(
    "attune_rag.model_tiers",
    reason="attune-rag [rag] extra absent or predates model_tiers; CI runs this",
)

from attune_author import model_tiers as author_tiers  # noqa: E402


def test_defaults_match_canonical() -> None:
    assert author_tiers._DEFAULTS == rag_tiers._DEFAULTS


def test_env_vars_match_canonical() -> None:
    assert author_tiers._ENV == rag_tiers._ENV


def test_known_models_match_canonical() -> None:
    assert author_tiers._KNOWN_MODELS == rag_tiers._KNOWN_MODELS


def test_fable_extras_match_canonical() -> None:
    for model in ("claude-fable-5", "claude-sonnet-5", "claude-haiku-4-5"):
        assert author_tiers.fable_extras(model) == rag_tiers.fable_extras(model)


def test_resolution_matches_canonical(monkeypatch: pytest.MonkeyPatch) -> None:
    for tier in author_tiers._DEFAULTS:
        monkeypatch.delenv(author_tiers._ENV[tier], raising=False)
        assert author_tiers.resolve_model(tier) == rag_tiers.resolve_model(tier)
        monkeypatch.setenv(author_tiers._ENV[tier], "claude-opus-4-8")
        assert author_tiers.resolve_model(tier) == rag_tiers.resolve_model(tier)
