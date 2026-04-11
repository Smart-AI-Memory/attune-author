"""Document generation stages: outline, write, review.

Each stage is a standalone function that takes source content
and configuration, calls the Anthropic API through the shared
helper in :mod:`attune_author.doc_gen._anthropic`, and returns
the result. The pipeline in ``pipeline.py`` orchestrates them.
"""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING

from attune_author.doc_gen._anthropic import (
    OUTLINE_SOURCE_CHARS,
    REVIEW_SOURCE_CHARS,
    WRITE_SOURCE_CHARS,
    call_anthropic,
)

if TYPE_CHECKING:
    from anthropic import Anthropic

logger = logging.getLogger(__name__)


def build_outline(
    client: Anthropic,
    source_content: str,
    doc_type: str,
    audience: str,
    model: str,
    max_tokens: int,
) -> str:
    """Generate a structured documentation outline.

    Args:
        client: Anthropic client instance.
        source_content: Source code to document.
        doc_type: Documentation type (api-reference, guide).
        audience: Target audience.
        model: Model ID for generation.
        max_tokens: Maximum tokens for the response.

    Returns:
        Outline text.
    """
    system = (
        "You are an expert technical writer. Create a detailed, "
        "structured outline for documentation.\n\n"
        "Include sections for:\n"
        "1. Overview/Introduction\n"
        "2. Quick Start example\n"
        "3. API Reference (functions and classes)\n"
        "4. Usage Examples\n"
        "5. Additional reference as needed\n\n"
        "Format as a numbered list with section titles and "
        "descriptions."
    )

    user_message = (
        f"Create a documentation outline:\n\n"
        f"Document Type: {doc_type}\n"
        f"Target Audience: {audience}\n\n"
        f"Source code:\n{source_content[:OUTLINE_SOURCE_CHARS]}\n\n"
        f"Generate a comprehensive outline."
    )

    return call_anthropic(
        client,
        system=system,
        user_message=user_message,
        model=model,
        max_tokens=max_tokens,
    )


def write_content(
    client: Anthropic,
    outline: str,
    source_content: str,
    doc_type: str,
    audience: str,
    model: str,
    max_tokens: int,
    section_focus: list[str] | None = None,
) -> str:
    """Write documentation content from an outline.

    Args:
        client: Anthropic client instance.
        outline: Documentation outline from outline stage.
        source_content: Original source code.
        doc_type: Documentation type.
        audience: Target audience.
        model: Model ID for generation.
        max_tokens: Maximum tokens for the response.
        section_focus: Specific sections to focus on.

    Returns:
        Draft documentation content.
    """
    focus_instruction = ""
    if section_focus:
        sections_list = ", ".join(section_focus)
        focus_instruction = f"\n\nFocus ONLY on these sections: {sections_list}"

    system = (
        f"You are an expert technical writer creating "
        f"documentation for {audience}.\n\n"
        f"Write clear, comprehensive documentation with:\n"
        f"- Real code examples from the source\n"
        f"- Complete API reference with parameter types\n"
        f"- Usage guides and best practices\n"
        f"- Error handling and edge cases"
        f"{focus_instruction}"
    )

    user_message = (
        f"Write documentation:\n\n"
        f"Document Type: {doc_type}\n"
        f"Audience: {audience}\n\n"
        f"Outline:\n{outline}\n\n"
        f"Source code:\n{source_content[:WRITE_SOURCE_CHARS]}\n\n"
        f"Generate complete documentation following the outline."
    )

    return call_anthropic(
        client,
        system=system,
        user_message=user_message,
        model=model,
        max_tokens=max_tokens,
    )


def review_content(
    client: Anthropic,
    draft: str,
    source_content: str,
    doc_type: str,
    audience: str,
    model: str,
    max_tokens: int,
) -> str:
    """Review and polish draft documentation.

    Args:
        client: Anthropic client instance.
        draft: Draft documentation to review.
        source_content: Original source code for accuracy.
        doc_type: Documentation type.
        audience: Target audience.
        model: Model ID for generation.
        max_tokens: Maximum tokens for the response.

    Returns:
        Polished documentation content, or the original draft
        if the review returned empty content.
    """
    system = (
        "You are a documentation reviewer. Polish the draft:\n\n"
        "- Fix inaccuracies against the source code\n"
        "- Improve clarity and consistency\n"
        "- Ensure code examples are correct and runnable\n"
        "- Check API reference completeness\n"
        "- Fix formatting and markdown structure\n\n"
        "Return the improved documentation only."
    )

    user_message = (
        f"Review and polish this {doc_type} documentation "
        f"for {audience}:\n\n"
        f"## Draft\n\n{draft}\n\n"
        f"## Source code (for accuracy)\n\n"
        f"{source_content[:REVIEW_SOURCE_CHARS]}\n\n"
        f"Return the polished documentation."
    )

    polished = call_anthropic(
        client,
        system=system,
        user_message=user_message,
        model=model,
        max_tokens=max_tokens,
    )
    return polished or draft


def parse_outline_sections(outline: str) -> list[str]:
    """Parse top-level section titles from an outline.

    Args:
        outline: Raw outline text.

    Returns:
        List of section title strings.
    """
    sections: list[str] = []
    top_level_pattern = re.compile(r"^(\d+)\.\s+([A-Za-z].*)")

    for line in outline.split("\n"):
        stripped = line.strip()
        match = top_level_pattern.match(stripped)
        if match:
            title = match.group(2).strip()
            if " - " in title:
                title = title.split(" - ")[0].strip()
            sections.append(title)

    return sections
