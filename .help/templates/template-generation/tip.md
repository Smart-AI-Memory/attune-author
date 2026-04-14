---
type: tip
feature: template-generation
depth: tip
generated_at: 2026-04-14T13:58:50.932279+00:00
source_hash: 83bb6e5c2f6907087e0db48de07d88ae3c21652d99c4be4964d15c1658289845
status: generated
---

# Use `generate_feature_templates()` for all template creation

## Recommendation

Call `generate_feature_templates()` instead of building templates manually or using internal functions. This function handles AST inspection, depth selection, and file generation in one operation.

## Why this matters

The generation pipeline has many moving parts — feature validation, source file discovery, template matching, and hash computation. The public API orchestrates these steps correctly and handles edge cases you might miss.

## Trade-offs

You lose fine-grained control over individual template types, but you gain consistency and avoid reimplementing the depth logic (`_CORE_DEPTH_NAMES` and template type constants).
