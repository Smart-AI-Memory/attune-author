---
type: tip
feature: template-generation
depth: tip
generated_at: 2026-04-14T16:03:43.022797+00:00
source_hash: 83bb6e5c2f6907087e0db48de07d88ae3c21652d99c4be4964d15c1658289845
status: generated
---

# Check source hashes to know when templates need regeneration

Use the `source_hash` field in `GeneratedTemplate` and `GenerationResult` to detect when your source code has changed since templates were last generated.

When you call `generate_feature_templates()`, it computes a hash of the analyzed source files and stores it in both the individual template results and the overall generation result. Compare this hash against previous runs to avoid regenerating templates unnecessarily, or to alert you when existing templates may be stale.

The hash changes whenever the source code structure that feeds template generation changes — not just any file modification, but changes to the classes, functions, and docstrings that the generator analyzes.
