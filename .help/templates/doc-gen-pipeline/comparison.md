---
type: comparison
feature: doc-gen-pipeline
depth: comparison
generated_at: 2026-04-11T05:01:53.227689+00:00
source_hash: dcd99211b2080853c45dbe17f061733f0b7ff80387279d574d2bd011d8114aa2
status: generated
---

# Doc Gen Pipeline vs single-stage generation

## Context

The doc-gen-pipeline breaks documentation generation into three deliberate stages: outline, write, and review. This contrasts with single-pass generation that produces final docs in one LLM call.

## Feature comparison

| Aspect | Doc Gen Pipeline | Single-stage generation |
|--------|------------------|-------------------------|
| **Quality** | Higher quality through iterative refinement | Variable, depends on prompt engineering |
| **Control** | Granular control over each stage | Limited to initial prompt configuration |
| **Debugging** | Can inspect outline and draft before final output | Black box - only see final result |
| **Cost** | 3x LLM calls per document | 1x LLM call per document |
| **Speed** | Slower due to sequential stages | Faster single-pass execution |
| **Consistency** | Structured outline ensures consistent coverage | Output structure varies by LLM interpretation |
| **Customization** | Can focus on specific sections via `section_focus` | Must regenerate entire document for changes |

## Use doc-gen-pipeline when

- **Quality matters more than speed** - You need polished documentation for public-facing or critical internal use
- **You need consistent structure** - Documentation should follow predictable patterns across multiple source files
- **You want to review intermediate outputs** - Ability to inspect the outline before committing to full generation is valuable
- **You're generating long-form content** - Complex documentation benefits from the planning stage that `build_outline()` provides
- **You need section-level control** - The `section_focus` parameter lets you regenerate specific parts without rewriting everything

## Use single-stage generation when

- **Speed is critical** - You need quick documentation for internal development or prototyping
- **Cost is a primary concern** - Your use case can't justify 3x the LLM API costs
- **Content is simple** - Short reference docs or basic API documentation don't need multi-stage refinement
- **You have excellent prompts already** - Your single-stage prompts consistently produce high-quality output

## Recommendation

Choose doc-gen-pipeline for production documentation workflows where quality and consistency justify the additional time and cost. The three-stage approach produces noticeably better results for complex documentation, and the intermediate outputs make debugging much easier when generation goes wrong.

For quick internal docs or when experimenting with documentation approaches, single-stage generation is often sufficient and much faster to iterate on.

## Source files

- `src/attune_author/doc_gen/pipeline.py`
- `src/attune_author/doc_gen/stages.py`
- `src/attune_author/doc_gen/config.py`

**Tags:** `doc-gen`, `pipeline`, `llm`, `multi-stage`
