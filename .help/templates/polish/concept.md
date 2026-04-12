---
type: concept
feature: polish
depth: concept
generated_at: 2026-04-12T04:18:19.239884+00:00
source_hash: 9f00fa4d4bf451430bdb559d13e2781477df4a00e9c10586bff49eaa38404dbc
status: generated
---

# Polish

Polish is an LLM-powered quality improvement system that rewrites auto-generated help templates to follow Google's developer documentation style guide.

## Core responsibilities

Polish transforms raw generated templates into polished documentation by:

- **Template refinement** — Rewrites formulaic auto-generated content into clear, concrete prose using template-specific system prompts
- **Source grounding** — Builds concise summaries from your codebase's public API to ensure accuracy and prevent hallucination
- **Style enforcement** — Applies Google's documentation standards, including second-person voice, active construction, and noun-phrase headings
- **Error handling** — Raises `PolishError` when the LLM pass fails in strict mode, allowing you to catch and handle quality issues

## Template specialization

The system tailors its approach based on template type. For example:
- Concept templates get prompts emphasizing mental models and concrete examples
- How-to guides receive prompts focused on clear step sequences
- Reference docs get prompts that prioritize accuracy and completeness

You configure this behavior through `get_system_prompt()`, which returns template-specific instructions and anti-patterns to avoid.

## Integration points

Other parts of the documentation system use polish through:

| Function | Purpose |
|----------|---------|
| `polish_template()` | Executes the LLM rewrite pass with source context and template-specific prompts |
| `build_source_summary()` | Creates accuracy-checking summaries from public classes, functions, and module docstrings |
