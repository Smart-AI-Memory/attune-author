---
type: reference
feature: polish
depth: reference
generated_at: 2026-04-12T04:18:36.927169+00:00
source_hash: 9f00fa4d4bf451430bdb559d13e2781477df4a00e9c10586bff49eaa38404dbc
status: generated
---

# Polish reference

## Classes

| Class | Description |
|-------|-------------|
| `PolishError` | Exception raised when LLM polish operations fail in strict mode |

## Functions

| Function | Description |
|----------|-------------|
| `polish_template()` | Sends generated templates to an LLM for style and clarity improvements |
| `build_source_summary()` | Creates structured summaries of source code for LLM context |
| `get_system_prompt()` | Retrieves template-specific prompting instructions for different documentation types |

## Source files

- `src/attune_author/polish.py`
- `src/attune_author/polish_prompts.py`
