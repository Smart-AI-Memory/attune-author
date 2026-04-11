"""LLM polish pass for generated help templates.

After Jinja2 renders the structural skeleton, this module
sends the content through an LLM to improve writing quality:
replace formulaic filler, sharpen descriptions, verify
accuracy against the source info provided.

Per-type system prompts live in :mod:`polish_prompts`. This
module owns the polish call orchestration, strict/lenient
mode handling, and the source-summary builder that feeds
context to the prompt. The underlying SDK call is routed
through :mod:`attune_author.doc_gen._anthropic` so that
credential redaction and error wrapping are shared with the
doc-gen pipeline.

Strict mode
-----------

Polish is strict by default: a missing ``ANTHROPIC_API_KEY``
or any LLM-call failure raises :class:`PolishError`. Polish
exists because the raw Jinja2 output is not acceptable on
its own; treating the LLM pass as best-effort would quietly
ship lower-quality templates.

Opting out of strict mode is explicit and deliberate:

1. Pass ``strict=False`` to :func:`polish_template` directly.
2. Set the ``ATTUNE_AUTHOR_STRICT_POLISH`` environment
   variable to a falsy value (``0``, ``false``, ``no``,
   ``off``) — useful for CI that runs the generator without
   credentials. The explicit ``strict`` argument always
   overrides the environment variable.
"""

from __future__ import annotations

import logging
import os

from attune_author.doc_gen._anthropic import (
    AnthropicCallError,
    call_anthropic,
    get_client,
)
from attune_author.polish_prompts import get_system_prompt

logger = logging.getLogger(__name__)

#: Environment variable that flips polish out of strict mode.
#: Strict is the default — this variable exists only as an
#: explicit opt-out for environments that genuinely cannot
#: run the LLM pass (e.g. CI without credentials).
STRICT_ENV_VAR = "ATTUNE_AUTHOR_STRICT_POLISH"

#: Values of ``STRICT_ENV_VAR`` that disable strict mode.
#: Anything else — unset, truthy, or unrecognized — keeps
#: strict behavior, which is the whole point of the flip.
_FALSY = frozenset({"0", "false", "no", "off"})


def _env_strict_default() -> bool:
    """Read the strict-mode default from the environment.

    Strict is the default. The environment variable exists
    only to let callers opt out by setting it to a falsy
    value.

    Returns:
        False if ``STRICT_ENV_VAR`` is explicitly set to a
        falsy value; True otherwise.
    """
    val = os.environ.get(STRICT_ENV_VAR, "").strip().lower()
    return val not in _FALSY


class PolishError(RuntimeError):
    """Raised when the polish pass fails in strict mode.

    Lenient mode never raises — it logs a warning and
    returns the original content.
    """


def polish_template(
    content: str,
    feature_name: str,
    source_summary: str,
    template_type: str = "generic",
    strict: bool | None = None,
) -> str:
    """Polish a generated template using an LLM.

    Args:
        content: The Jinja2-rendered markdown, including
            YAML frontmatter.
        feature_name: Name of the feature being documented.
            Used in the user-message context.
        source_summary: Summary of source info (classes,
            functions, signatures, docstrings) built by
            :func:`build_source_summary`. Serves as the
            accuracy anchor for the LLM rewrite.
        template_type: Template kind being polished —
            concept, task, reference, error, warning,
            troubleshooting, faq, or ``"generic"`` as a
            fallback. Controls which system prompt the LLM
            sees.
        strict: If True (the default when ``None``), any
            failure in the polish pass (missing API key,
            network error, SDK error) raises
            :class:`PolishError`. If False, failures fall
            back to returning the original content. When
            ``None``, the value is read from the
            ``ATTUNE_AUTHOR_STRICT_POLISH`` environment
            variable, which defaults to strict.

    Returns:
        Polished markdown string, or the original content
        if polish failed and strict mode is off.

    Raises:
        PolishError: If the polish pass fails and strict
            mode is enabled.
    """
    effective_strict = _env_strict_default() if strict is None else strict

    try:
        polished = _call_llm(content, feature_name, source_summary, template_type)
        return _sanitize_output(polished)
    except Exception as exc:  # noqa: BLE001
        # INTENTIONAL: lenient mode swallows any LLM failure
        # so that `attune-author` can still run without an
        # API key when the caller has explicitly opted out.
        # Strict mode (the default) rewraps everything in
        # PolishError so callers have a single exception
        # type to catch.
        if effective_strict:
            raise PolishError(
                f"Polish pass failed for {feature_name!r} " f"(type={template_type!r}): {exc}"
            ) from exc
        logger.warning(
            "Polish pass failed for %s (type=%s), using raw template: %s",
            feature_name,
            template_type,
            exc,
        )
        return content


def _sanitize_output(content: str) -> str:
    """Apply trailing-whitespace and newline hygiene.

    The Anthropic API does not guarantee a trailing newline
    and occasionally leaves trailing whitespace on
    individual lines (most often from markdown ``  `` line
    breaks the model emits in tables and lists). Both of
    these break the no-trailing-whitespace and
    single-trailing-newline invariants the rest of the
    pipeline enforces, so we normalize them here.

    Args:
        content: Raw text returned by the LLM.

    Returns:
        Content with each line right-stripped and exactly
        one trailing newline.
    """
    if not content:
        return content
    body = "\n".join(line.rstrip() for line in content.splitlines())
    if not body.endswith("\n"):
        body += "\n"
    return body


def _call_llm(
    content: str,
    feature_name: str,
    source_summary: str,
    template_type: str,
) -> str:
    """Make the LLM call for polishing.

    Delegates client creation and the SDK invocation to the
    shared helper in :mod:`attune_author.doc_gen._anthropic`
    so that credential handling and error redaction stay in
    one place.

    Args:
        content: Template content to polish.
        feature_name: Feature name for context.
        source_summary: Source code summary.
        template_type: Template kind — selects system prompt.

    Returns:
        Polished content from LLM, or the original content
        when the LLM returned an empty response.

    Raises:
        AnthropicCallError: If no API key is available or
            the SDK call fails.
    """
    client = get_client()
    system_prompt = get_system_prompt(template_type)

    user_message = (
        f"Polish this auto-generated {template_type} template "
        f"for the '{feature_name}' feature.\n\n"
        f"## Source info (for accuracy checking)\n\n"
        f"{source_summary}\n\n"
        f"## Template to polish\n\n"
        f"{content}"
    )

    polished = call_anthropic(
        client,
        system=system_prompt,
        user_message=user_message,
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
    )
    return polished or content


# Re-export so callers can catch a single exception type
# regardless of whether the failure came from the SDK call
# or from the wrapping polish layer.
__all__ = [
    "AnthropicCallError",
    "PolishError",
    "STRICT_ENV_VAR",
    "_env_strict_default",
    "build_source_summary",
    "polish_template",
]


def build_source_summary(
    public_classes: list[dict[str, str]],
    public_functions: list[dict[str, str]],
    module_docstrings: list[str],
    file_count: int,
    function_signatures: list[dict[str, str]] | None = None,
    class_signatures: list[dict[str, str]] | None = None,
) -> str:
    """Build a concise source summary for the polish prompt.

    Produces a structured summary the LLM can use as an
    accuracy anchor: module purposes, classes, functions,
    and — when available — their signatures. The summary
    is deliberately capped: the prompt context is more
    useful when it fits in a few hundred tokens than when
    it dominates the call.

    Args:
        public_classes: Class dicts with name/doc/file.
            Kept for backward compatibility when the
            signature list is not provided.
        public_functions: Function dicts with name/doc/file.
        module_docstrings: First lines of module docstrings.
        file_count: Total number of source files.
        function_signatures: Optional list of function dicts
            with name/signature/doc/file keys. When provided,
            overrides ``public_functions`` for the Functions
            section to give the LLM argument and return
            type context.
        class_signatures: Optional list of class dicts with
            name/methods/doc/file keys. ``methods`` is a
            newline-separated string of method signatures.
            When provided, augments the Classes section with
            method details.

    Returns:
        Formatted summary string, designed to sit comfortably
        within a single LLM prompt without dominating it.
    """
    parts: list[str] = []

    if module_docstrings:
        parts.append("Module purposes:")
        for doc in module_docstrings[:5]:
            parts.append(f"  - {doc}")

    classes = class_signatures or [
        {"name": c["name"], "doc": c.get("doc", ""), "methods": ""} for c in public_classes
    ]
    if classes:
        parts.append("")
        parts.append("Classes:")
        for cls in classes[:10]:
            doc = cls.get("doc", "")
            name = cls["name"]
            parts.append(f"  - {name}" + (f": {doc}" if doc else ""))
            methods = cls.get("methods", "").strip()
            if methods:
                for method_line in methods.splitlines():
                    stripped = method_line.strip()
                    if stripped:
                        parts.append(f"      {stripped}")

    functions = function_signatures or [
        {
            "name": f["name"],
            "signature": "",
            "doc": f.get("doc", ""),
        }
        for f in public_functions
    ]
    if functions:
        parts.append("")
        parts.append("Functions:")
        for fn in functions[:10]:
            sig = fn.get("signature", "").strip()
            doc = fn.get("doc", "")
            if sig:
                header = f"  - {sig}"
            else:
                header = f"  - {fn['name']}()"
            if doc:
                header = f"{header} — {doc}"
            parts.append(header)

    parts.append("")
    parts.append(f"Total source files: {file_count}")

    return "\n".join(parts)
