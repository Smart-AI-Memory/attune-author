---
type: comparison
feature: doc-gen-pipeline
depth: comparison
generated_at: 2026-04-14T14:14:52.197689+00:00
source_hash: 6474cc0d69cd0c4e82d4326b3b640d5a2a68fcfc45b228e045a8cca9f9c93b0b
status: generated
---

# Doc Gen Pipeline vs single-pass generation

## Context

The doc gen pipeline uses a three-stage process (outline → write → review) to generate documentation, while most LLM tools generate content in a single pass. This structured approach trades speed for quality by giving the model explicit planning and revision steps.

## Feature comparison

| Aspect | Doc Gen Pipeline | Single-pass generation |
|--------|------------------|------------------------|
| **Quality** | Higher consistency via structured stages | Variable, depends on prompt quality |
| **Speed** | ~3x slower due to multiple API calls | Fast, one API call |
| **Token usage** | Higher total consumption across stages | Lower, single request |
| **Configurability** | Fine-grained control per stage (outline: 1k, write: 8k, review: 8k tokens) | Limited to single prompt configuration |
| **Error recovery** | Can retry individual stages | Must restart entire generation |
| **Output structure** | Predictable via outline-driven writing | Less predictable structure |
| **Section focus** | Can target specific sections via `section_focus` | Must emphasize in single prompt |

## Use the doc gen pipeline when

- **Documentation quality matters more than speed** — The three-stage process produces more structured, comprehensive output
- **You're generating long-form content** — The outline stage prevents the model from losing track of structure in complex documents
- **You need consistent formatting** — The pipeline enforces a planning phase that standardizes output structure
- **You're automating documentation workflows** — The structured result object (`DocGenResult`) integrates cleanly with build systems

## Use single-pass generation when

- **You need quick drafts** — Simple content that doesn't justify the pipeline overhead
- **Token costs are a primary concern** — Single requests use fewer tokens than multi-stage processing
- **You're generating short content** — Brief API docs or simple explanations don't benefit from the outline phase
- **You need real-time interaction** — The pipeline's multiple API calls create noticeable latency

## Configuration advantages

The pipeline's `DocGenConfig` gives you granular control:

```python
config = DocGenConfig(
    doc_type='tutorial',           # vs 'api-reference'
    audience='beginners',          # vs 'developers'
    max_outline_tokens=1500,       # Longer planning phase
    sections_per_chunk=2,          # Smaller write batches
    section_focus=['examples']     # Emphasize specific content
)
```

Single-pass tools typically offer only prompt-level customization.

## Recommendation

**Choose the doc gen pipeline for production documentation workflows** where quality and consistency outweigh speed concerns. The structured approach justifies its overhead for anything longer than a function docstring or simple README section.

Use single-pass generation for quick drafts, prototyping, or when integrating documentation into fast development loops where the three-stage process would interrupt flow.

## Source files

- `src/attune_author/doc_gen/pipeline.py`
- `src/attune_author/doc_gen/stages.py`
- `src/attune_author/doc_gen/config.py`

**Tags:** `doc-gen`, `pipeline`, `llm`, `multi-stage`
