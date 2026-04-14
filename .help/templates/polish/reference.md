---
type: reference
feature: polish
depth: reference
generated_at: 2026-04-14T16:04:34.689909+00:00
source_hash: 39a4215a31cf6bfa17f5b898ad071827d406cbe4dc8d2744f17fe7fd680d6891
status: generated
---

# Polish reference

Polish auto-generated help templates using LLM-based style improvements and template-specific prompting.

## Classes

| Class | Description |
|-------|-------------|
| `PolishError` | Raised when the polish pass fails in strict mode |

## Functions

| Function | Parameters | Returns | Raises | Description |
|----------|------------|---------|---------|-------------|
| `polish_template` | `content: str, feature_name: str, source_summary: str, template_type: str = 'generic', strict: bool \| None = None` | `str` | `PolishError` | Polish a generated template using an LLM |
| `build_source_summary` | `public_classes: list[dict[str, str]], public_functions: list[dict[str, str]], module_docstrings: list[str], file_count: int, function_signatures: list[dict[str, str]] \| None = None, class_signatures: list[dict[str, str]] \| None = None, module_constants: list[dict[str, object]] \| None = None` | `str` | | Build a concise source summary for the polish prompt |
| `get_system_prompt` | `template_type: str` | `str` | | Build the system prompt for a given template kind |

### Raises

| Exception | Message |
|-----------|---------|
| `PolishError` | 'Polish pass failed for {...} (type={...}): {...}' |

## Constants

| Constant | Value | Description |
|----------|--------|-------------|
| `STRICT_ENV_VAR` | `'ATTUNE_AUTHOR_STRICT_POLISH'` | Environment variable controlling strict polish mode |
| `_FALSY` | `{'0', 'false', 'no', 'off'}` | String values that disable strict mode |
| `_BASE_RULES` | `'You are a technical writer following Google\'s developer\ndocumentation style guide...'` | Base system prompt rules for all template types |
