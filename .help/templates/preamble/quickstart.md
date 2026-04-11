---
type: quickstart
feature: preamble
depth: quickstart
generated_at: 2026-04-11T04:56:21.860331+00:00
source_hash: 3e02ceee37af71750f50dd40ecd95359ea5c4aaf1a1a7e50691cfb6250d133b0
status: generated
---

# Quickstart: preamble

```python
from attune_author.preamble import get_preamble

preamble = get_preamble("auth")
print(preamble)
# Output: "Handle user authentication and session management"
```

## Prerequisites

- The project is cloned and installed locally

## Get your first preamble

1. **Import the function:**
   ```python
   from attune_author.preamble import get_preamble
   ```

2. **Request a preamble for any feature:**
   ```python
   preamble = get_preamble("database")
   print(preamble)
   ```

3. **Find related features:**
   ```python
   from attune_author.preamble import get_related_preambles

   related = get_related_preambles("database", max_results=3)
   for item in related:
       print(f"{item['feature']}: {item['preamble']}")
   ```

You'll see one-line descriptions that provide context for each workflow skill based on your project's current state.

**Next:** Check the concept page to learn how preambles adapt to your project's activity patterns.
