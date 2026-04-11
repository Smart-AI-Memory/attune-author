---
type: tip
feature: preamble
depth: tip
generated_at: 2026-04-11T04:56:28.344357+00:00
source_hash: 3e02ceee37af71750f50dd40ecd95359ea5c4aaf1a1a7e50691cfb6250d133b0
status: generated
---

# Cache preamble lookups to avoid redundant filesystem reads

## Context

The preamble module fetches context-sensitive one-liners for workflow skills, but each call to `get_preamble()` and `get_related_preambles()` reads from disk.

## Recommendation

Store the results of preamble lookups in a simple dictionary keyed by feature name. Since preambles rarely change during a session, this eliminates repeated file system access for the same feature.

Cache misses are cheap (one file read), but cache hits save noticeable time when you're repeatedly querying the same features or their related items.

**Tradeoff**: You'll need to clear the cache manually if preamble content changes during development, but production workflows typically query each feature only once.

## Source files

- `src/attune_author/preamble.py`

**Tags:** `context`, `rendering`, `workflow`
