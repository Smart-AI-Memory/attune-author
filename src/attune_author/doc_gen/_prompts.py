"""System prompts for the three doc-gen stages.

Each stage of the doc-gen pipeline (outline, write, review)
sends its own system prompt to the Anthropic SDK. Keeping the
prompts in one module — instead of inlined inside ``stages.py``
— mirrors the pattern used by :mod:`attune_author.polish_prompts`
and lets the prompts be inspected, tested, and rewritten without
touching the stage call sites.

The shared opening (``You are an expert technical writer``) lives
in :data:`_BASE_VOICE` so that future tone changes only have to
land in one place.
"""

from __future__ import annotations

#: Shared opening clause used by every doc-gen stage. Pulling
#: it out means the writer-voice description does not drift
#: across stages when one of them is rewritten.
_BASE_VOICE = "You are an expert technical writer"


OUTLINE_SYSTEM = (
    f"{_BASE_VOICE}. Create a detailed, structured outline for "
    "documentation.\n\n"
    "Include sections for:\n"
    "1. Overview/Introduction\n"
    "2. Quick Start example\n"
    "3. API Reference (functions and classes)\n"
    "4. Usage Examples\n"
    "5. Additional reference as needed\n\n"
    "Format as a numbered list with section titles and descriptions."
)


def write_system(audience: str, focus_instruction: str = "") -> str:
    """Build the system prompt for the write stage.

    The write stage interpolates the audience into its prompt and
    optionally narrows the writer to a subset of sections, so it
    cannot be a static constant the way the other two are.

    Args:
        audience: Target audience name (e.g. ``"developers"``).
        focus_instruction: Pre-formatted "Focus ONLY on..." clause,
            or the empty string when no narrowing is requested.

    Returns:
        The fully assembled system prompt for the write stage.
    """
    return (
        f"{_BASE_VOICE} creating documentation for {audience}.\n\n"
        "Write clear, comprehensive documentation with:\n"
        "- Real code examples from the source\n"
        "- Complete API reference with parameter types\n"
        "- Usage guides and best practices\n"
        "- Error handling and edge cases"
        f"{focus_instruction}"
    )


REVIEW_SYSTEM = (
    "You are a documentation reviewer. Polish the draft:\n\n"
    "- Fix inaccuracies against the source code\n"
    "- Improve clarity and consistency\n"
    "- Ensure code examples are correct and runnable\n"
    "- Check API reference completeness\n"
    "- Fix formatting and markdown structure\n\n"
    "Return the improved documentation only."
)


__all__ = [
    "OUTLINE_SYSTEM",
    "REVIEW_SYSTEM",
    "write_system",
]
