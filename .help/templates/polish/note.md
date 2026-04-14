---
type: note
feature: polish
depth: note
generated_at: 2026-04-14T16:05:50.676708+00:00
source_hash: 39a4215a31cf6bfa17f5b898ad071827d406cbe4dc8d2744f17fe7fd680d6891
status: generated
---

# Note: polish

## Context

The polish feature improves generated template quality through an LLM rewrite pass. It uses template-specific system prompts and source code summaries to ensure the polished output remains factually accurate while improving readability and following Google's developer documentation style guide.

## Content

The polish feature centers on the `polish_template()` function, which takes a generated template and returns an improved version. The function uses Claude via Anthropic's API to rewrite content while preserving structural elements like YAML frontmatter and h1 titles.

Supporting functions include:
- `build_source_summary()` — Creates concise summaries of source code for inclusion in polish prompts
- `get_system_prompt()` — Returns template-type-specific prompts (concept, task, reference, or note)

The `PolishError` exception is raised when polishing fails in strict mode. Strict mode is controlled by the `ATTUNE_AUTHOR_STRICT_POLISH` environment variable and determines whether polish failures should halt execution or be silently ignored.

The system prompts in `polish_prompts.py` include base rules that apply to all template types plus specific guidance for each template kind. For example, note templates should be factual rather than instructional, while task templates should use imperative voice and focus on user goals.

## Source files

- `src/attune_author/polish.py`
- `src/attune_author/polish_prompts.py`

**Tags:** `polish`, `llm`, `anthropic`, `quality`
