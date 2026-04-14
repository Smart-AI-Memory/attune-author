---
type: reference
feature: polish
depth: reference
generated_at: 2026-04-14T13:59:43.325466+00:00
source_hash: cc9d97e96d238e30cf1d9fe96dacf73df94080aa66763e646494a334efc5ce52
status: generated
---

# Polish reference

The polish feature provides LLM-powered quality improvement for auto-generated help templates, with per-template-type system prompts and configurable error handling.

## Classes

| Class | Description |
|-------|-------------|
| `PolishError` | Raised when the polish pass fails in strict mode |

## Functions

| Function | Parameters | Returns | Raises |
|----------|------------|---------|---------|
| `polish_template` | `content: str, feature_name: str, source_summary: str, template_type: str = 'generic', strict: bool \| None = None` | `str` | `PolishError` — 'Polish pass failed for {...} (type={...}): {...}' |
| `build_source_summary` | `public_classes: list[dict[str, str]], public_functions: list[dict[str, str]], module_docstrings: list[str], file_count: int, function_signatures: list[dict[str, str]] \| None = None, class_signatures: list[dict[str, str]] \| None = None, module_constants: list[dict[str, object]] \| None = None` | `str` | |
| `get_system_prompt` | `template_type: str` | `str` | |

## Constants

| Constant | Value |
|----------|-------|
| `STRICT_ENV_VAR` | `'ATTUNE_AUTHOR_STRICT_POLISH'` |

## Internal constants

| Constant | Members |
|----------|---------|
| `FALSY` | `'0', 'false', 'no', 'off'` |
