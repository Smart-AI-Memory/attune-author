"""Tests for the PR 2 polish improvements.

Covers the three distinct additions to the polish pass:

- Per-type system prompts via :mod:`polish_prompts`
- Strict mode via the ``strict=`` kwarg and the
  ``ATTUNE_AUTHOR_STRICT_POLISH`` environment variable
- Signature-aware source summaries via
  :func:`build_source_summary`
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from attune_author.polish import (
    STRICT_ENV_VAR,
    PolishError,
    _env_strict_default,
    build_source_summary,
    polish_template,
)
from attune_author.polish_prompts import (
    ANTI_PATTERNS,
    SYSTEM_PROMPTS,
    get_system_prompt,
)

# ---------------------------------------------------------
# Per-type prompts
# ---------------------------------------------------------


class TestPerTypePrompts:
    """System-prompt selection by template kind."""

    @pytest.mark.parametrize(
        "kind",
        ["concept", "task", "reference", "error", "warning", "troubleshooting", "faq"],
    )
    def test_prompt_exists_for_every_kind(self, kind: str) -> None:
        """Every template kind produced by the generator has
        a corresponding system prompt.
        """
        prompt = get_system_prompt(kind)
        assert prompt
        assert len(prompt) > 100, "Prompt suspiciously short"

    def test_prompt_includes_base_rules(self) -> None:
        """Base rules appear in every per-kind prompt."""
        for kind in SYSTEM_PROMPTS:
            prompt = SYSTEM_PROMPTS[kind]
            assert "frontmatter" in prompt
            assert "second person" in prompt
            assert "Do not invent features" in prompt

    @pytest.mark.parametrize(
        "kind,expected_phrase",
        [
            ("concept", "definition"),
            ("task", "Use ... when"),
            ("reference", "noun phrases"),
            ("error", "exception types"),
            ("warning", "pitfall"),
            ("troubleshooting", "symptom table"),
            ("faq", "plain language"),
        ],
    )
    def test_kind_guidance_differentiates_prompts(
        self, kind: str, expected_phrase: str
    ) -> None:
        """Each kind-specific prompt contains a phrase that
        uniquely identifies its intent — guards against
        silent regression to the pre-PR 2 single prompt.
        """
        prompt = SYSTEM_PROMPTS[kind]
        assert (
            expected_phrase in prompt
        ), f"{kind} prompt missing expected guidance: {expected_phrase!r}"

    def test_unknown_kind_falls_back_to_base(self) -> None:
        """An unknown template kind returns the base rules
        without the per-kind section or anti-patterns.
        """
        prompt = get_system_prompt("totally-fake-kind")
        assert "frontmatter" in prompt
        # No kind-specific heading should appear
        for phrase in ("You are polishing a CONCEPT", "You are polishing a TASK"):
            assert phrase not in prompt

    def test_anti_patterns_embedded_in_prompt(self) -> None:
        """Anti-pattern phrases appear verbatim in the system
        prompt for their kind — this is what teaches the LLM
        to avoid formulaic boilerplate.
        """
        for kind, patterns in ANTI_PATTERNS.items():
            prompt = SYSTEM_PROMPTS[kind]
            for phrase in patterns:
                assert (
                    phrase in prompt
                ), f"{kind}: anti-pattern {phrase!r} missing from prompt"


# ---------------------------------------------------------
# Strict mode
# ---------------------------------------------------------


class TestStrictMode:
    """Strict-mode behavior for polish_template."""

    def test_strict_true_raises_on_missing_key(self) -> None:
        """strict=True raises PolishError when no API key."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(PolishError, match="Polish pass failed"):
                polish_template(
                    "content",
                    "feature",
                    "summary",
                    template_type="concept",
                    strict=True,
                )

    def test_strict_false_falls_back_to_original(self) -> None:
        """strict=False returns the original content on failure."""
        with patch.dict("os.environ", {}, clear=True):
            result = polish_template(
                "original",
                "feature",
                "summary",
                template_type="concept",
                strict=False,
            )
            assert result == "original"

    def test_strict_none_reads_env_var(self) -> None:
        """strict=None consults the env var — truthy value
        enables strict mode.
        """
        with patch.dict("os.environ", {STRICT_ENV_VAR: "1"}, clear=True):
            with pytest.raises(PolishError):
                polish_template(
                    "content",
                    "feature",
                    "summary",
                    template_type="concept",
                    # strict omitted on purpose
                )

    def test_strict_none_without_env_is_lenient(self) -> None:
        """strict=None with no env var falls through silently."""
        with patch.dict("os.environ", {}, clear=True):
            result = polish_template(
                "original",
                "feature",
                "summary",
                template_type="concept",
            )
            assert result == "original"

    def test_explicit_strict_false_overrides_env(self) -> None:
        """An explicit strict=False overrides the env var
        when both are present.
        """
        with patch.dict("os.environ", {STRICT_ENV_VAR: "1"}, clear=True):
            result = polish_template(
                "original",
                "feature",
                "summary",
                template_type="concept",
                strict=False,
            )
            assert result == "original"

    @pytest.mark.parametrize("value", ["1", "true", "TRUE", "yes", "Yes", "on"])
    def test_env_var_truthy_values(self, value: str) -> None:
        """All documented truthy env-var values enable strict
        mode.
        """
        with patch.dict("os.environ", {STRICT_ENV_VAR: value}, clear=True):
            assert _env_strict_default() is True

    @pytest.mark.parametrize("value", ["", "0", "false", "no", "off", "maybe"])
    def test_env_var_falsy_values(self, value: str) -> None:
        """Empty or non-truthy env-var values leave strict
        mode off.
        """
        with patch.dict("os.environ", {STRICT_ENV_VAR: value}, clear=True):
            assert _env_strict_default() is False

    def test_strict_mode_wraps_sdk_errors(self) -> None:
        """Strict mode re-raises anthropic SDK errors as
        PolishError with the original exception chained.
        """
        with patch.dict(
            "os.environ", {"ANTHROPIC_API_KEY": "fake"}
        ):  # pragma: allowlist secret
            with patch("attune_author.polish._call_llm") as mock_call:
                mock_call.side_effect = ValueError("sdk blew up")
                with pytest.raises(PolishError) as exc_info:
                    polish_template(
                        "content",
                        "feature",
                        "summary",
                        template_type="concept",
                        strict=True,
                    )
                assert exc_info.value.__cause__ is not None
                assert "sdk blew up" in str(exc_info.value.__cause__)


# ---------------------------------------------------------
# Per-type prompt passthrough
# ---------------------------------------------------------


class TestPolishTemplateUsesPerTypePrompt:
    """Verify the correct system prompt reaches the SDK."""

    def test_call_llm_passes_kind_specific_prompt(self) -> None:
        """The system prompt sent to Anthropic should be the
        one for the requested template_type.
        """
        from attune_author.polish import _call_llm

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="polished")]

        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response

        with patch.dict(
            "os.environ", {"ANTHROPIC_API_KEY": "fake"}
        ):  # pragma: allowlist secret
            with patch("anthropic.Anthropic", return_value=mock_client):
                _call_llm("content", "feature", "summary", "troubleshooting")

        call_kwargs = mock_client.messages.create.call_args.kwargs
        sent_system = call_kwargs["system"]
        assert "TROUBLESHOOTING" in sent_system
        assert "symptom table" in sent_system

    def test_call_llm_includes_template_type_in_user_message(self) -> None:
        """The user message mentions the template type so the
        LLM can disambiguate when multiple kinds share a
        feature name.
        """
        from attune_author.polish import _call_llm

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="polished")]

        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response

        with patch.dict(
            "os.environ", {"ANTHROPIC_API_KEY": "fake"}
        ):  # pragma: allowlist secret
            with patch("anthropic.Anthropic", return_value=mock_client):
                _call_llm("content", "myfeature", "summary", "warning")

        call_kwargs = mock_client.messages.create.call_args.kwargs
        user_msg = call_kwargs["messages"][0]["content"]
        assert "warning template" in user_msg
        assert "myfeature" in user_msg


# ---------------------------------------------------------
# Signature-aware source summaries
# ---------------------------------------------------------


class TestSignatureAwareSourceSummary:
    """Tests for the enriched build_source_summary path."""

    def test_function_signatures_surface_types(self) -> None:
        """When function_signatures is provided, the summary
        shows typed signatures instead of bare names.
        """
        result = build_source_summary(
            public_classes=[],
            public_functions=[],
            module_docstrings=[],
            file_count=1,
            function_signatures=[
                {
                    "name": "authenticate",
                    "signature": "authenticate(user: str, password: str) -> bool",
                    "doc": "Authenticate a user",
                    "file": "auth.py",
                },
            ],
        )
        assert "authenticate(user: str, password: str) -> bool" in result
        assert "Authenticate a user" in result

    def test_class_signatures_show_methods(self) -> None:
        """When class_signatures is provided, each class
        entry includes its public method signatures.
        """
        result = build_source_summary(
            public_classes=[],
            public_functions=[],
            module_docstrings=[],
            file_count=1,
            class_signatures=[
                {
                    "name": "AuthService",
                    "doc": "Authentication",
                    "methods": (
                        "__init__(self, db: str)\n"
                        "login(self, user: str, pw: str) -> bool\n"
                        "logout(self) -> None"
                    ),
                    "file": "auth.py",
                },
            ],
        )
        assert "AuthService" in result
        assert "__init__(self, db: str)" in result
        assert "login(self, user: str, pw: str) -> bool" in result
        assert "logout(self) -> None" in result

    def test_signatures_override_legacy_lists(self) -> None:
        """When both legacy lists and signature lists are
        provided, the signature lists win — the summary
        should not double-print the function/class entries.
        """
        result = build_source_summary(
            public_classes=[{"name": "LegacyFoo", "doc": "legacy"}],
            public_functions=[{"name": "legacy_fn", "doc": "legacy doc"}],
            module_docstrings=[],
            file_count=1,
            function_signatures=[
                {
                    "name": "new_fn",
                    "signature": "new_fn(x: int) -> int",
                    "doc": "new function",
                },
            ],
            class_signatures=[
                {"name": "NewFoo", "doc": "new", "methods": ""},
            ],
        )
        assert "NewFoo" in result
        assert "new_fn(x: int) -> int" in result
        assert "LegacyFoo" not in result
        assert "legacy_fn" not in result

    def test_legacy_lists_still_work_when_signatures_missing(self) -> None:
        """Passing only the legacy lists produces output that
        matches the pre-PR 2 behavior.
        """
        result = build_source_summary(
            public_classes=[{"name": "Foo", "doc": "Foo class"}],
            public_functions=[{"name": "bar", "doc": "bar function"}],
            module_docstrings=[],
            file_count=2,
        )
        assert "Foo: Foo class" in result
        assert "bar() — bar function" in result

    def test_summary_caps_to_ten_entries(self) -> None:
        """Long function lists are truncated so the summary
        does not dominate the LLM prompt.
        """
        signatures = [
            {
                "name": f"fn_{i}",
                "signature": f"fn_{i}(x: int) -> int",
                "doc": "",
            }
            for i in range(20)
        ]
        result = build_source_summary(
            public_classes=[],
            public_functions=[],
            module_docstrings=[],
            file_count=20,
            function_signatures=signatures,
        )
        assert "fn_0" in result
        assert "fn_9" in result
        assert "fn_15" not in result

    def test_empty_signatures_do_not_emit_section(self) -> None:
        """An empty signature list should not produce an
        empty ``Functions:`` heading.
        """
        result = build_source_summary(
            public_classes=[],
            public_functions=[],
            module_docstrings=[],
            file_count=0,
            function_signatures=[],
            class_signatures=[],
        )
        assert "Functions:" not in result
        assert "Classes:" not in result


# ---------------------------------------------------------
# Signature extraction from AST
# ---------------------------------------------------------


class TestGeneratorSignatureExtraction:
    """Tests for the _format_function_signature helper that
    feeds the enriched source summary.
    """

    def test_simple_function(self) -> None:
        """A function with typed args and return annotation."""
        import ast

        from attune_author.generator import _format_function_signature

        tree = ast.parse("def foo(x: int, y: str) -> bool: ...")
        node = tree.body[0]
        assert isinstance(node, ast.FunctionDef)
        sig = _format_function_signature(node)
        assert sig == "foo(x: int, y: str) -> bool"

    def test_function_with_defaults(self) -> None:
        """Default values are preserved in the signature."""
        import ast

        from attune_author.generator import _format_function_signature

        tree = ast.parse("def foo(x: int, y: bool = False) -> None: ...")
        node = tree.body[0]
        assert isinstance(node, ast.FunctionDef)
        sig = _format_function_signature(node)
        assert "y: bool = False" in sig

    def test_function_with_kwonly_args(self) -> None:
        """Keyword-only args appear after ``*``."""
        import ast

        from attune_author.generator import _format_function_signature

        tree = ast.parse("def foo(x: int, *, y: str = 'a') -> None: ...")
        node = tree.body[0]
        assert isinstance(node, ast.FunctionDef)
        sig = _format_function_signature(node)
        assert "*" in sig
        assert "y: str = 'a'" in sig

    def test_function_without_annotations(self) -> None:
        """Unannotated args appear without type hints."""
        import ast

        from attune_author.generator import _format_function_signature

        tree = ast.parse("def foo(x, y): ...")
        node = tree.body[0]
        assert isinstance(node, ast.FunctionDef)
        sig = _format_function_signature(node)
        assert sig == "foo(x, y)"

    def test_async_function(self) -> None:
        """Async functions produce a plain signature (the
        ``async`` prefix is not currently in the output —
        it's the call-site context that matters).
        """
        import ast

        from attune_author.generator import _format_function_signature

        tree = ast.parse("async def foo(x: int) -> int: ...")
        node = tree.body[0]
        assert isinstance(node, ast.AsyncFunctionDef)
        sig = _format_function_signature(node)
        assert sig == "foo(x: int) -> int"

    def test_class_methods_extracted(self) -> None:
        """Public methods are included; dunders other than
        __init__ are skipped.
        """
        import ast

        from attune_author.generator import _format_class_methods

        tree = ast.parse(
            "class Foo:\n"
            "    def __init__(self, x: int): ...\n"
            "    def public(self) -> None: ...\n"
            "    def _private(self) -> None: ...\n"
            "    def __hash__(self) -> int: ...\n"
        )
        node = tree.body[0]
        assert isinstance(node, ast.ClassDef)
        methods = _format_class_methods(node)
        assert "__init__" in methods
        assert "public(self) -> None" in methods
        assert "_private" not in methods
        assert "__hash__" not in methods
