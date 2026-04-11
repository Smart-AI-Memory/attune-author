---
type: reference
feature: preamble
depth: reference
generated_at: 2026-04-11T04:55:37.555599+00:00
source_hash: 3e02ceee37af71750f50dd40ecd95359ea5c4aaf1a1a7e50691cfb6250d133b0
status: generated
---

# Preamble reference

## Functions

| Function | Description | Parameters | Return Type |
|----------|-------------|------------|-------------|
| `get_preamble()` | Get the one-liner preamble for a feature | `feature_name: str`, `help_dir: str \| Path \| None = None` | `str \| None` |
| `get_related_preambles()` | Get preambles for features related by shared tags | `feature_name: str`, `help_dir: str \| Path \| None = None`, `max_results: int = 3` | `list[dict[str, str]]` |

## Source files

- `src/attune_author/preamble.py`

## Tags

`context`, `rendering`, `workflow`
