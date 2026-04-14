---
type: reference
feature: preamble
depth: reference
generated_at: 2026-04-14T16:12:37.307649+00:00
source_hash: 4b502067010f8654195a342453668853d3f231f8ca87c84c441ba90da1f2b064
status: generated
---

# Preamble reference

Access context-sensitive preambles for workflow skills.

## Functions

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `get_preamble()` | `feature_name: str, help_dir: str \| Path \| None = None` | `str \| None` | Get the one-liner preamble for a feature. |
| `get_related_preambles()` | `feature_name: str, help_dir: str \| Path \| None = None, max_results: int = 3` | `list[dict[str, str]]` | Get preambles for features related by shared tags. |

## Source files

- `src/attune_author/preamble.py`

## Tags

`context`, `rendering`, `workflow`
