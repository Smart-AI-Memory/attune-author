---
type: reference
feature: polish
depth: reference
generated_at: 2026-04-26T19:47:19.826246+00:00
source_hash: c3c5a14decb406edb1b2d8ca09a6adb5d3bf68908f60cdaf9a9ea6ba0df1471d
status: generated
---

# Polish reference

Polish generated help templates using an LLM to improve readability, structure, and adherence to Google's developer documentation style guide.

## Classes

| Class | Description |
|-------|-------------|
| `PolishError` | Raised when the polish pass fails in strict mode |

## Functions

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `polish_template()` | `content: str, feature_name: str, source_summary: str, template_type: str = "generic", strict: bool \| None = None, augmented_context: str \| None = None` | `str` | Polish a generated template using an LLM |
| `build_source_summary()` | `public_classes: list[dict[str, str]], public_functions: list[dict[str, str]], module_docstrings: list[str], file_count: int, function_signatures: list[dict[str, str]] \| None = None, class_signatures: list[dict[str, str]] \| None = None, module_constants: list[dict[str, object]] \| None = None` | `str` | Build a concise source summary for the polish prompt |
| `get_system_prompt()` | `template_type: str` | `str` | Build the system prompt for a given template kind |

### Raises

| Function | Exception | Message |
|----------|-----------|---------|
| `polish_template()` | `PolishError` | `'Polish pass failed for {...} (type={...}): {...}'` |

## Constants

| Constant | Values | Description |
|----------|--------|-------------|
| `STRICT_ENV_VAR` | `'ATTUNE_AUTHOR_STRICT_POLISH'` | Environment variable name for enabling strict mode |
| `_FALSY` | `{'0', 'false', 'no', 'off'}` | String values that disable strict mode |
| `_BASE_RULES` | System prompt base rules | Core polishing instructions applied to all template types |

## Tags

`polish`, `llm`, `anthropic`, `quality`
