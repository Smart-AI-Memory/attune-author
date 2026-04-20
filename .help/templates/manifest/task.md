---
type: task
feature: manifest
depth: task
generated_at: 2026-04-14T16:06:23.468307+00:00
source_hash: 9a254478123a04daeb294db1576d4b58b18d970e577f6263f65fa33be54c42ee
status: generated
---

# Work with manifest

Use the manifest module when you need to load, validate, or query the .help/features.yaml file that maps project features to source files.

## Prerequisites

- Access to the project source code
- Familiarity with the files under src/attune_author/manifest.py

## Load a features.yaml manifest

1. **Import the load_manifest function:**
   ```python
   from attune_author.manifest import load_manifest
   ```

2. **Call load_manifest with your .help/ directory path:**
   ```python
   manifest = load_manifest("path/to/.help")
   ```

3. **Access the loaded features:**
   ```python
   for feature_name, feature in manifest.features.items():
       print(f"{feature_name}: {feature.description}")
   ```

The function raises `FileNotFoundError` if features.yaml doesn't exist and `ValueError` for invalid manifest format.

## Save a manifest to features.yaml

1. **Create or modify a FeatureManifest:**
   ```python
   from attune_author.manifest import FeatureManifest, Feature, save_manifest

   feature = Feature(
       name="auth",
       description="User authentication system",
       files=["src/auth/*.py"],
       tags=["security"]
   )

   manifest = FeatureManifest(
       version=1,
       features={"auth": feature}
   )
   ```

2. **Write the manifest to disk:**
   ```python
   saved_path = save_manifest(manifest, "path/to/.help")
   ```

The function returns the path where the manifest was saved.

## Match changed files to features

1. **Get your list of changed files:**
   ```python
   changed_files = ["src/auth/login.py", "src/auth/tokens.py"]
   ```

2. **Match them against feature patterns:**
   ```python
   from attune_author.manifest import match_files_to_features

   matches = match_files_to_features(changed_files, manifest)
   ```

3. **Process the results:**
   ```python
   for feature_name, matched_files in matches.items():
       print(f"Feature '{feature_name}' affected by: {matched_files}")
   ```

## Resolve a user query to a feature

1. **Use resolve_topic to find the best feature match:**
   ```python
   from attune_author.manifest import resolve_topic

   feature_name = resolve_topic("authentication", manifest)
   if feature_name:
       print(f"Query 'authentication' maps to feature: {feature_name}")
   ```

The function returns `None` if no feature matches the query.

## Validate feature names

1. **Check if a feature name is safe for file paths:**
   ```python
   from attune_author.manifest import is_safe_feature_name

   if is_safe_feature_name("my-feature"):
       print("Safe to use as filename")
   else:
       print("Contains unsafe characters")
   ```

This prevents names with path separators, null bytes, or relative path components.

## Verify success

Run `pytest -k "manifest"` to confirm your changes don't break existing functionality. Your manifest operations succeed when:

- `load_manifest()` returns a FeatureManifest object without exceptions
- `save_manifest()` writes a valid features.yaml file
- `match_files_to_features()` returns expected feature-to-files mappings
- `resolve_topic()` finds the correct feature for your queries

## Key files

- `src/attune_author/manifest.py` — All manifest parsing and querying functions
