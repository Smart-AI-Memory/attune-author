---
type: comparison
feature: doc-gen-pipeline
depth: comparison
generated_at: 2026-04-14T16:19:47.609448+00:00
source_hash: 6474cc0d69cd0c4e82d4326b3b640d5a2a68fcfc45b228e045a8cca9f9c93b0b
status: generated
---

# Doc Gen Pipeline vs direct LLM calls

## Context

The doc-gen-pipeline implements a three-stage approach (outline → write → review) for generating documentation, while you could also call an LLM directly in a single step. Both produce documentation, but they differ significantly in output quality, token usage, and control.

## Feature comparison

| Aspect | Doc Gen Pipeline | Direct LLM calls |
|--------|------------------|------------------|
| **Output quality** | Higher quality through iterative refinement | Variable, depends on prompt engineering |
| **Token usage** | ~17,000 tokens total across 3 stages | ~8,000 tokens in single call |
| **Structure consistency** | Enforced through outline stage | Relies on prompt instructions |
| **Debugging** | Inspectable intermediate outputs (outline, draft) | Single black-box output |
| **Customization** | Section focus via `section_focus` parameter | Full prompt control |
| **Error recovery** | Can retry individual stages | Must restart entire process |
| **Setup complexity** | Configure `DocGenConfig`, handle 3 API calls | Single API call with custom prompt |

## Use doc gen pipeline when...

Choose the pipeline approach for production documentation where quality matters:

- **You need consistent structure** across multiple documents
- **Quality trumps speed** — the three-stage process takes ~3x the tokens but produces more polished output
- **You're generating API references or tutorials** where missing information is costly
- **You want to inspect intermediate steps** for debugging or fine-tuning

The pipeline excels at complex documentation types like API references, where the outline stage ensures comprehensive coverage and the review stage catches technical inaccuracies.

## Use direct LLM calls when...

Skip the pipeline for simpler scenarios:

- **You're prototyping** documentation formats or experimenting with prompts
- **Token budget is tight** — you need documentation but can't afford 17k tokens per document
- **You have domain-specific requirements** that need custom prompting beyond what `section_focus` provides
- **Speed matters more than polish** for internal docs or quick reference materials

Direct calls work well for simple explanations, code comments expansion, or when you already have a proven prompt that produces good results.

## Recommendation

**Use doc gen pipeline** as your default for any documentation that will be read by others. The quality improvement from the three-stage process usually justifies the extra token cost. Only drop down to direct LLM calls when you have specific constraints (budget, custom prompting needs) or you're in exploration mode.

## Source files

- `src/attune_author/doc_gen/pipeline.py`
- `src/attune_author/doc_gen/stages.py`
- `src/attune_author/doc_gen/config.py`

**Tags:** `doc-gen`, `pipeline`, `llm`, `multi-stage`
