---
type: warning
feature: manifest
depth: warning
generated_at: 2026-04-14T16:07:00.572347+00:00
source_hash: 9a254478123a04daeb294db1576d4b58b18d970e577f6263f65fa33be54c42ee
status: generated
---

# Manifest cautions

## What to watch for

The manifest system parses and queries `.help/features.yaml` files to map project features to source files. Several operations can fail silently or produce unexpected results.

## Risk areas

### File path validation bypasses

`is_safe_feature_name()` only blocks obvious path traversal tokens (`/`, `\`, `..`, null bytes). Feature names like `con`, `aux`, or names with trailing spaces can still cause filesystem issues on Windows or when used in URLs.

**Mitigation:** Validate feature names against your deployment targets, not just the basic safety check.

### Manifest loading failures mask root causes

`load_manifest()` raises generic `ValueError` messages for multiple error conditions. When debugging manifest issues, the error "Invalid manifest at path: expected mapping" could mean malformed YAML, wrong file encoding, or permission problems.

**Mitigation:** Check file permissions and encoding before investigating YAML structure. Use `yaml.safe_load()` directly to isolate parsing issues.

### File matching depends on glob behavior

`match_files_to_features()` uses Python's glob patterns to match file paths. Patterns like `src/**/*.py` behave differently than shell globs - they won't match files in the root `src/` directory itself.

**Mitigation:** Test glob patterns with actual file paths before committing them to the manifest. Remember that `**` requires at least one directory separator.

### Topic resolution uses fuzzy matching

`resolve_topic()` attempts to match user queries to feature names, but the matching algorithm isn't documented. Queries might resolve to unexpected features when names are similar.

**Mitigation:** Use exact feature names in automation. Reserve fuzzy queries for interactive use only.

## How to avoid problems

1. **Validate manifests in CI.** Add a build step that calls `load_manifest()` on all feature manifests to catch YAML errors before deployment.

2. **Test file patterns with real paths.** Before adding new glob patterns to feature files, verify they match your intended files using Python's `glob` module directly.

3. **Handle FileNotFoundError explicitly.** Don't assume `.help/features.yaml` exists. Provide clear fallback behavior when projects lack feature manifests.

## Source files

- `src/attune_author/manifest.py`

**Tags:** `configuration`, `yaml`, `features`
