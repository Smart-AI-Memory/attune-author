---
type: comparison
feature: polish
depth: comparison
generated_at: 2026-04-14T14:01:05.582917+00:00
source_hash: cc9d97e96d238e30cf1d9fe96dacf73df94080aa66763e646494a334efc5ce52
status: generated
---

# Comparison: Polish vs alternatives

## Context

The polish feature improves generated template quality through an LLM-powered rewrite pass. It uses template-specific system prompts and source-grounded summaries to transform raw auto-generated documentation into polished, readable content.

## Polish vs manual editing

| Feature | Polish | Manual editing |
|---------|---------|---------------|
| Speed | Processes templates in seconds | Requires human time per template |
| Consistency | Uses standardized prompts for each template type | Varies by editor and their availability |
| Source accuracy | Validates against provided source summary | Risk of drift from actual implementation |
| Customization | Limited to prompt engineering | Full editorial control |
| Error handling | Strict mode with `PolishError` exceptions | Human judgment prevents most errors |

Polish excels at bulk template improvement and maintaining consistency across large documentation sets. Manual editing offers complete control but doesn't scale well.

## Polish vs other documentation tools

Most documentation generators stop at raw template creation. Polish bridges the gap between auto-generation and publication-ready content by applying editorial intelligence at scale.

Unlike static template systems, polish adapts its approach based on template type — comparison pages get different treatment than troubleshooting guides.

## When to use polish

Use polish when you need to:

- **Transform bulk generated content** — Polish processes multiple templates consistently using the same quality standards
- **Maintain source accuracy** — The `build_source_summary()` function ensures edits stay grounded in actual implementation details
- **Apply template-specific improvements** — Different template types get specialized system prompts through `get_system_prompt()`
- **Catch polish failures early** — Strict mode raises `PolishError` exceptions when the LLM pass doesn't meet quality thresholds

## When manual editing is better

Skip polish when you need:

- **Deep structural changes** — Polish improves existing structure but doesn't redesign template organization
- **Domain-specific expertise** — Complex technical concepts may need human subject matter experts
- **One-off customizations** — For single templates with unique requirements, direct editing is faster
- **No LLM access** — Polish requires Anthropic API access; manual editing works offline

## Use polish when...

Your documentation workflow involves generating many templates that need consistent editorial improvement, and you want to maintain accuracy while scaling beyond what manual editing can handle. If you're processing fewer than 10 templates or need deep structural changes, manual editing is likely more efficient.
