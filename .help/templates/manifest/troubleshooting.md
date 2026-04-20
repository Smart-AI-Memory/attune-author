---
type: troubleshooting
feature: manifest
depth: troubleshooting
generated_at: 2026-04-14T16:07:15.917123+00:00
source_hash: 9a254478123a04daeb294db1576d4b58b18d970e577f6263f65fa33be54c42ee
status: generated
---

# Troubleshoot manifest

## Before you start

The manifest feature parses and queries the `.help/features.yaml` file that defines project features and their associated files. This troubleshooting guide helps you diagnose issues with loading, saving, or querying the features manifest.

## Symptom table

| If you observe | Check |
|----------------|-------|
| `FileNotFoundError: No {...} in {...}` | Verify `features.yaml` exists in the `.help/` directory |
| `ValueError: Invalid manifest` or `expected mapping, got {...}` | Open `features.yaml` and check for valid YAML syntax |
| `ValueError: Invalid feature name: {...}` | Check feature names for unsafe characters: `/`, `\`, `..`, or null bytes |
| `ValueError: feature '...' must be a mapping` | Ensure each feature entry has `name`, `description`, and optional `files`/`tags` fields |
| Empty results from `match_files_to_features()` | Verify file paths match the glob patterns in feature `files` lists |
| `resolve_topic()` returns `None` | Check that your query matches existing feature names or descriptions |

## Step-by-step diagnosis

1. **Reproduce the issue with minimal input.**
   Create a simple test case that isolates the failing operation. For example, if `load_manifest()` fails, try loading just the problematic `.help/` directory without other application context.

2. **Validate the features.yaml structure.**
   Open `.help/features.yaml` and verify it follows this format:
   ```yaml
   version: 1
   features:
     feature-name:
       name: "Display Name"
       description: "What this feature does"
       files: ["path/pattern/*.py"]
       tags: ["tag1", "tag2"]
   ```

3. **Check feature names for safety.**
   Run `is_safe_feature_name()` on any problematic feature names. Unsafe names contain `/`, `\`, `..`, or null bytes.

4. **Examine specific function behavior:**
   - **`load_manifest()`**: Check file permissions and YAML syntax
   - **`save_manifest()`**: Verify write permissions to the `.help/` directory
   - **`match_files_to_features()`**: Test file path patterns against actual file paths
   - **`resolve_topic()`**: Compare your query string against existing feature names and descriptions

5. **Run related tests.**
   Execute `pytest -k "manifest" -v` to see which manifest tests pass or fail. Working tests can provide examples of correct usage.

## Common fixes

- **Fix YAML syntax errors.** Use a YAML validator to check `.help/features.yaml` for syntax issues like incorrect indentation or missing colons.

- **Sanitize feature names.** Replace unsafe characters in feature names:
  ```bash
  # Remove or replace problematic characters
  sed -i 's/[\/\\]/-/g' .help/features.yaml
  ```

- **Update file glob patterns.** If `match_files_to_features()` returns empty results, adjust the `files` patterns in your feature definitions to match your actual file structure.

- **Recreate missing manifest.** If `features.yaml` is missing or corrupted:
  ```python
  from attune_author.manifest import FeatureManifest, save_manifest

  manifest = FeatureManifest(version=1, features={})
  save_manifest(manifest, ".help/")
  ```

- **Check directory permissions.** Ensure the `.help/` directory is readable for loading and writable for saving manifests.

## Source files

- `src/attune_author/manifest.py`

**Tags:** `configuration`, `yaml`, `features`
