---
type: comparison
feature: polish
depth: comparison
generated_at: 2026-04-11T04:49:38.662927+00:00
source_hash: 024a299e9a8252b83e070c5a5297e1292dd243e8eddc631dcf298bae31fb8dc0
status: generated
---

# Polish vs manual editing

## Context

The polish feature improves auto-generated help templates through an LLM rewrite pass. It uses specialized system prompts for different template types and includes source code summaries to keep the output accurate.

## Feature comparison

| Feature | Polish | Manual editing |
|---------|--------|----------------|
| **Speed** | Seconds per template | Minutes to hours per template |
| **Consistency** | Enforces style guide rules automatically | Depends on editor knowledge and attention |
| **Accuracy** | Source-grounded with built-in fact checking | Risk of introducing errors or outdated info |
| **Customization** | Template-type specific prompts only | Full control over content and structure |
| **Scale** | Handles batch processing easily | Becomes bottleneck for large projects |
| **Learning curve** | Requires LLM API setup | Uses existing writing skills |

## When to use polish

Use the polish feature when:

- **You have many templates to improve** — The automated approach scales better than manual editing for projects with 10+ help files
- **Consistency matters** — Polish applies Google's developer documentation style guide uniformly across all templates
- **You want accuracy guarantees** — The source summary prevents the LLM from inventing features or capabilities
- **Speed trumps perfect customization** — A good-enough result in seconds beats a perfect result in 30 minutes

Key functions for this workflow:

- `polish_template()` — The main entry point that takes raw template content and returns improved markdown
- `build_source_summary()` — Generates factual summaries from your codebase to ground the LLM rewrite
- `get_system_prompt()` — Retrieves template-specific style instructions

## When NOT to use polish

Stick with manual editing when:

- **You need deep customization** — Polish follows fixed patterns and cannot make creative structural changes
- **Your templates are already high quality** — The improvement may not justify the LLM API costs
- **You lack LLM API access** — The feature requires external service integration
- **Content accuracy is critical** — LLMs can occasionally misinterpret source code despite grounding safeguards

## Use polish when...

Choose polish for routine template improvement at scale. It excels at transforming auto-generated drafts into readable documentation while preserving technical accuracy. Manual editing remains better for high-stakes content that needs human judgment or creative restructuring.

The 80/20 rule applies here: polish handles 80% of improvement work automatically, leaving you to focus manual effort on the 20% that truly needs human insight.

## Source files

- `src/attune_author/polish.py`
- `src/attune_author/polish_prompts.py`

**Tags:** `polish`, `llm`, `anthropic`, `quality`
