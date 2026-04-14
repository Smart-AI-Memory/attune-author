---
type: quickstart
feature: preamble
depth: quickstart
generated_at: 2026-04-14T16:13:24.615980+00:00
source_hash: 4b502067010f8654195a342453668853d3f231f8ca87c84c441ba90da1f2b064
status: generated
---

# Quickstart: preamble

```python
from attune_author.preamble import get_preamble

preamble = get_preamble("workflow")
print(preamble)
```

## Prerequisites

- Python environment with attune_author installed
- Access to feature help files (or use default locations)

## Display a feature preamble

1. **Import and call `get_preamble()`** with any feature name:

```python
from attune_author.preamble import get_preamble

# Get a one-liner description for a feature
preamble = get_preamble("workflow")
print(preamble)
# Output: "Coordinate multi-step processes with state tracking and recovery"
```

2. **Find related features** using shared tags:

```python
from attune_author.preamble import get_related_preambles

related = get_related_preambles("workflow", max_results=2)
for item in related:
    print(f"{item['feature']}: {item['preamble']}")
# Output:
# state: "Manage persistent data across workflow steps"
# recovery: "Resume interrupted workflows from checkpoints"
```

3. **Handle missing features** gracefully:

```python
missing = get_preamble("nonexistent_feature")
print(missing)  # Output: None
```

## Next

Read the [preamble concept guide](../concepts/preamble.md) to understand how preambles are generated from help file metadata.
