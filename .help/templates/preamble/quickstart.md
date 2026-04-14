---
type: quickstart
feature: preamble
depth: quickstart
generated_at: 2026-04-14T14:08:27.187006+00:00
source_hash: 4b502067010f8654195a342453668853d3f231f8ca87c84c441ba90da1f2b064
status: generated
---

# Quickstart: preamble

```python
from attune_author.preamble import get_preamble

preamble = get_preamble("authentication")
print(preamble)
```

## Prerequisites

- Python environment with `attune_author` installed
- Access to help documentation files (optional for basic usage)

## Steps

1. **Import the preamble module** and call `get_preamble()` with any feature name:

   ```python
   from attune_author.preamble import get_preamble

   preamble = get_preamble("authentication")
   print(preamble)
   ```

   Expected output: A one-line description of the authentication feature, or `None` if no preamble exists.

2. **Find related features** using shared tags:

   ```python
   from attune_author.preamble import get_related_preambles

   related = get_related_preambles("authentication", max_results=3)
   for item in related:
       print(f"{item['feature']}: {item['preamble']}")
   ```

   Expected output: Up to 3 feature names with their preambles, related by common tags.

3. **Specify a custom help directory** if your documentation lives elsewhere:

   ```python
   preamble = get_preamble("workflow", help_dir="/path/to/docs")
   ```

**Next:** Read the concept guide to understand how preambles are generated from feature metadata.
