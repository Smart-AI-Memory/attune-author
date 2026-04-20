---
type: comparison
feature: manifest
depth: comparison
generated_at: 2026-04-14T16:08:03.988482+00:00
source_hash: 9a254478123a04daeb294db1576d4b58b18d970e577f6263f65fa33be54c42ee
status: generated
---

# Manifest vs direct YAML parsing

## Context

The manifest feature handles parsing and querying the `.help/features.yaml` file that defines project features. You could alternatively use a generic YAML library or build custom parsing logic.

## Comparison

| Aspect | Manifest feature | Raw YAML parsing | Custom parser |
|--------|------------------|------------------|---------------|
| **Validation** | Built-in schema validation for feature structure | Manual validation required | You implement validation |
| **File matching** | `match_files_to_features()` with glob patterns | No file matching capabilities | You implement file matching |
| **Query resolution** | `resolve_topic()` handles fuzzy matching | No query capabilities | You implement search logic |
| **Safety checks** | `is_safe_feature_name()` prevents path traversal | No safety validation | You implement safety checks |
| **Error handling** | Specific error messages for common mistakes | Generic YAML parsing errors | Custom error messages |
| **Type safety** | Structured `Feature` and `FeatureManifest` dataclasses | Raw dictionaries | Your custom types |

## Use manifest when...

- You need to load or modify the project's feature definitions
- You want to match changed files against feature patterns
- You're building tools that query features by name or topic
- You need validation that catches malformed feature definitions
- You want protection against unsafe feature names that could cause path issues

The manifest API is specifically designed for this project's feature organization system. If you're working with `.help/features.yaml`, use this feature rather than rolling your own parser.

## Use raw YAML parsing when...

- You're working with other YAML files in the project (not `features.yaml`)
- You need parsing capabilities that the manifest feature doesn't provide
- You're building temporary scripts that don't need the full feature model

## Use a custom parser when...

You shouldn't. The manifest feature already handles the complexity of validating feature definitions, matching file patterns, and resolving queries. Building custom parsing logic duplicates this work and misses edge cases that the manifest feature already handles.

## Source files

- `src/attune_author/manifest.py`

**Tags:** `configuration`, `yaml`, `features`
