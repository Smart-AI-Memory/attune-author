---
type: reference
feature: polish
depth: reference
generated_at: 2026-04-11T04:48:21.899053+00:00
source_hash: 024a299e9a8252b83e070c5a5297e1292dd243e8eddc631dcf298bae31fb8dc0
status: generated
---

# Polish reference

## Classes

| Class | Description |
|-------|-------------|
| `PolishError` | Raised when the polish pass fails in strict mode |

## Functions

| Function | Description |
|----------|-------------|
| `polish_template()` | Refines generated help templates using LLM processing |
| `build_source_summary()` | Creates concise source summaries for polish prompts |
| `get_system_prompt()` | Retrieves template-specific system prompts for polish operations |

## Parameters

### polish_template()

| Parameter | Type | Description |
|-----------|------|-------------|
| `content` | `str` | Template content to polish |
| `feature_name` | `str` | Name of the feature being documented |
| `source_summary` | `str` | Summary of source code for context |
| `template_type` | `str` | Template kind (defaults to 'generic') |
| `strict` | `bool \| None` | Whether to raise errors on polish failures |

### build_source_summary()

| Parameter | Type | Description |
|-----------|------|-------------|
| `public_classes` | `list[dict[str, str]]` | Public class information |
| `public_functions` | `list[dict[str, str]]` | Public function information |
| `module_docstrings` | `list[str]` | Module-level documentation |
| `file_count` | `int` | Number of source files |
| `function_signatures` | `list[dict[str, str]] \| None` | Function signature details |
| `class_signatures` | `list[dict[str, str]] \| None` | Class signature details |

### get_system_prompt()

| Parameter | Type | Description |
|-----------|------|-------------|
| `template_type` | `str` | Template kind to get prompt for |
