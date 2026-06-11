"""Smoke test pinning the polish wire-level model name.

Lives outside the broader polish test suite specifically to
catch the next model-rename failure immediately. When Anthropic
deprecates the current model alias and we need to bump
`_POLISH_MODEL` again, this test fires a clear "the wire
contract is stale" signal so the bump is mechanical.

The test mocks at ``attune_author.doc_gen._anthropic.call_anthropic``
so no API tokens are spent.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from attune_author.polish import _POLISH_MODEL, polish_template

# The current value the codebase is pinned to. Update *both* this
# constant and `_POLISH_MODEL` together when migrating; the
# co-located assertion catches half-migrations where someone
# bumps one and forgets the other.
_EXPECTED_MODEL = "claude-sonnet-4-6"


def test_polish_model_constant_matches_expected() -> None:
    """Sentinel: ``_POLISH_MODEL`` is the model alias we expect.

    Failure mode: someone bumped the constant in source without
    bumping ``_EXPECTED_MODEL`` here. Update both together.
    """
    assert _POLISH_MODEL == _EXPECTED_MODEL


def test_polish_template_calls_sdk_with_expected_model() -> None:
    """Wire-contract test: the model passed to ``call_anthropic``
    matches ``_POLISH_MODEL`` (and thus our expected alias).

    Pinning the wire-level call shape — not just the constant —
    catches refactors that bypass the constant or pin the
    model elsewhere in the call site.

    Forces a cache miss via patched ``_cache_get`` so the LLM
    call path always runs (otherwise on a hot polish cache the
    SDK never gets called).
    """
    with patch("attune_author.polish._cache_get", return_value=None):
        with patch(
            "attune_author.doc_gen._anthropic.call_anthropic", return_value="polished body"
        ) as mock_call:
            with patch("attune_author.doc_gen._anthropic.get_client") as mock_client:
                mock_client.return_value = object()
                result = polish_template(
                    content="# Sample\n\nBody.\n",
                    feature_name="sample",
                    source_summary="def f(): pass",
                    template_type="concept",
                    strict=True,
                )

    # polish_template runs _sanitize_output, which may add a trailing newline.
    # Assert content rather than exact equality so the test isn't brittle.
    assert result.strip() == "polished body"
    mock_call.assert_called_once()
    kwargs = mock_call.call_args.kwargs
    assert kwargs["model"] == _EXPECTED_MODEL, (
        f"polish call went out with model={kwargs['model']!r}, "
        f"expected {_EXPECTED_MODEL!r}. If the model was intentionally bumped, "
        "update _EXPECTED_MODEL in tests/test_polish_smoke.py."
    )


def test_polish_template_uses_constant_not_hardcoded() -> None:
    """Belt-and-suspenders: re-pinning ``_POLISH_MODEL`` to a
    different value flows through to the SDK call.

    If someone hard-codes a model name at the call site instead
    of reading the constant, this test fails because the call
    will use the constant we monkey-patched but the assertion
    expects the new value.
    """
    sentinel = "claude-test-sentinel-9"
    with patch("attune_author.polish._cache_get", return_value=None):
        with patch("attune_author.polish._POLISH_MODEL", sentinel):
            with patch(
                "attune_author.doc_gen._anthropic.call_anthropic", return_value="ok"
            ) as mock_call:
                with patch("attune_author.doc_gen._anthropic.get_client") as mock_client:
                    mock_client.return_value = object()
                    polish_template(
                        content="# X\n\nY\n",
                        feature_name="x",
                        source_summary="",
                        template_type="concept",
                        strict=True,
                    )

    assert mock_call.call_args.kwargs["model"] == sentinel


def test_doc_gen_config_default_model_matches_expected() -> None:
    """Same sentinel for the second polish-adjacent code path:
    the `attune-author docs` subcommand uses `DocGenConfig.model`
    as its default model. Bumps must keep it aligned with the
    polish constant.
    """
    from attune_author.doc_gen import DocGenConfig

    assert DocGenConfig().model == _EXPECTED_MODEL, (
        f"DocGenConfig default model is {DocGenConfig().model!r}, "
        f"expected {_EXPECTED_MODEL!r}. The two model pins should track together."
    )


@pytest.mark.parametrize(
    "deprecated_alias",
    [
        # Historical: previously-pinned model that hit EOL 2026-06-15.
        # Re-using this list as a regression seed if we ever migrate again.
        "claude-sonnet-4-20250514",
    ],
)
def test_no_deprecated_model_aliases_in_constants(deprecated_alias: str) -> None:
    """Ensure deprecated aliases don't sneak back via copy-paste."""
    from attune_author.doc_gen import DocGenConfig

    assert _POLISH_MODEL != deprecated_alias
    assert DocGenConfig().model != deprecated_alias
