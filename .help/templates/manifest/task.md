---
type: task
feature: manifest
depth: task
generated_at: 2026-04-26T19:47:39.795204+00:00
source_hash: 83a32541b2c8d0a608f767253efe855779cf22ea2a49e097f20091f1c34012c2
status: generated
---

# Work with manifest

Use the manifest module when you need to read, validate, or update the `.help/features.yaml` file that defines your project's feature structure.

## Prerequisites

- Access to the project source code
- Python environment with the attune_help package installed
- Basic understanding of YAML structure

## Import the manifest module

```python
from attune_help.manifest import load_manifest, save_manifest, match_files_to_features
```

## Load an existing manifest

1. **Call `load_manifest()`** with the path to your `.help/features.yaml` file:

   ```python
   manifest = load_manifest('.help/features.yaml')
   ```

2. **Access the features** through the manifest object:

   ```python
   for feature in manifest.features:
       print(f"Feature: {feature.name}")
       print(f"Files: {feature.files}")
   ```

## Match source files to features

1. **Use `match_files_to_features()`** to automatically detect which source files belong to which features:

   ```python
   file_matches = match_files_to_features(source_files, manifest.features)
   ```

2. **Review the matches** to ensure accuracy before updating your manifest.

## Save changes to the manifest

1. **Modify the manifest object** as needed by adding, removing, or updating features.

2. **Save the updated manifest** back to the YAML file:

   ```python
   save_manifest(manifest, '.help/features.yaml')
   ```

## Verify the changes

Check that your `.help/features.yaml` file contains the expected feature definitions and file mappings. The manifest should validate against the expected schema and all referenced files should exist in your project.
