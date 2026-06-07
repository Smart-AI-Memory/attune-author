---
feature: polish
depth: reference
generated_at: 2026-06-06T23:19:48.567369+00:00
source_hash: 79da77a01c4b4a11716e33f5673ee64882fe6354c51b6cf999aee80d9dbe4b7e
status: generated
---

# Polish reference

## Classes

| Class | Description | File |
|-------|-------------|------|
| `PolishError` | Raised when the polish pass fails in strict mode. | `src/attune_author/polish.py` |
| `PolishCacheStats` | Aggregate prompt-cache token usage across polish calls. | `src/attune_author/polish.py` |

## Functions

| Function | Description | File |
|----------|-------------|------|
| `clear_cache()` | Delete every entry in the polish cache directory. | `src/attune_author/polish.py` |
| `polish_template()` | Polish a generated template using an LLM. | `src/attune_author/polish.py` |
| `build_polish_prompt()` | Build the (system_prompt, user_message) pair for a polish call. | `src/attune_author/polish.py` |
| `reset_polish_cache_telemetry()` | Reset the per-process prompt-cache telemetry counters. | `src/attune_author/polish.py` |
| `polish_cache_stats()` | Snapshot the current per-process prompt-cache aggregate. | `src/attune_author/polish.py` |
| `format_polish_cache_summary()` | End-of-run summary line, or ``None`` if polish never ran. | `src/attune_author/polish.py` |
| `build_source_summary()` | Build a concise source summary for the polish prompt. | `src/attune_author/polish.py` |
| `get_system_prompt()` | Build the system prompt for a given template kind. | `src/attune_author/polish_prompts.py` |


## Source files

- `src/attune_author/polish.py`
- `src/attune_author/polish_prompts.py`

## Tags

`polish`, `llm`, `anthropic`, `quality`
