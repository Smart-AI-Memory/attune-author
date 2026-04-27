---
type: concept
feature: polish
depth: concept
generated_at: 2026-04-26T19:46:57.016050+00:00
source_hash: c3c5a14decb406edb1b2d8ca09a6adb5d3bf68908f60cdaf9a9ea6ba0df1471d
status: generated
---

# Polish

## What

Polish is an LLM-powered editing pass that transforms auto-generated help templates into clear, readable documentation that follows Google's style guide.

When the help system generates a template from source code, it produces functional but mechanical content. The polish pass rewrites this draft using template-type-specific prompts and source code summaries to ensure the output reads naturally while staying technically accurate.

## Why

Raw generated templates suffer from three quality problems:

1. **Formulaic language** — Phrases like "manages core functionality" and "provides key capabilities" appear in every draft regardless of what the code actually does
2. **Poor structure** — Auto-generated sections follow a rigid pattern that doesn't adapt to the specific content being documented
3. **Missing context** — The generator knows what functions exist but not why they matter or how they fit together

Polish addresses these by applying human writing standards through AI, producing templates that read as if written by a technical writer who understands both the code and the audience.

## Core components

The polish system has three main parts:

**Template-specific prompts** — Each of the 11 template types gets its own system prompt with targeted guidance. Concept templates focus on mental models and noun-phrase headings. Task templates emphasize step-by-step clarity. Reference templates prioritize completeness and lookup efficiency.

**Source summaries** — Rather than sending raw code to the LLM, polish builds concise summaries highlighting public classes, functions, module purposes, and key constants. This keeps the context focused and prevents hallucination.

**Error handling** — The `PolishError` exception captures polish failures in strict mode, allowing the system to fall back to unpolished content rather than blocking generation entirely.

## Quality safeguards

Polish operates under strict constraints to prevent content drift:

- Preserves YAML frontmatter exactly as generated
- Maintains the h1 title and section structure intent
- Uses only information present in the source summary
- Returns pure markdown with no additional commentary

The `STRICT_ENV_VAR` setting controls whether polish failures stop generation or allow fallback to draft content.
