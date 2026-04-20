---
type: tip
feature: manifest
depth: tip
generated_at: 2026-04-14T16:07:50.687313+00:00
source_hash: 9a254478123a04daeb294db1576d4b58b18d970e577f6263f65fa33be54c42ee
status: generated
---

# Tip: working effectively with manifest

## Use `resolve_topic()` for user queries instead of direct feature lookups

When users ask about a feature by name, call `resolve_topic(query, manifest)` rather than looking up `manifest.features[query]` directly. The resolver handles partial matches and common variations, making your interface more forgiving.

**Why:** Direct dictionary lookups fail silently on typos or incomplete feature names, while the resolver gives users a better experience.

**Tradeoff:** The resolver adds a function call, but the fuzzy matching logic is complex enough that you don't want to reimplement it.

## Source files

- `src/attune_author/manifest.py`

**Tags:** `configuration`, `yaml`, `features`
