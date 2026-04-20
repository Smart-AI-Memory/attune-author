---
type: quickstart
feature: manifest
depth: quickstart
generated_at: 2026-04-14T16:07:44.218436+00:00
source_hash: 9a254478123a04daeb294db1576d4b58b18d970e577f6263f65fa33be54c42ee
status: generated
---

# Quickstart: manifest

```python
from attune_author.manifest import load_manifest

manifest = load_manifest(".help")
print(f"Found {len(manifest.features)} features")
```

Load and query your project's features.yaml manifest to understand which features map to which source files.

## Load your manifest

1. **Import the loader:**
   ```python
   from attune_author.manifest import load_manifest
   ```

2. **Load features.yaml:**
   ```python
   manifest = load_manifest(".help")
   ```

3. **Inspect the features:**
   ```python
   for name, feature in manifest.features.items():
       print(f"{name}: {len(feature.files)} files")
   ```

Expected output:
```
auth: 3 files
database: 7 files
api: 12 files
```

## Query features by file changes

Match changed files against feature patterns:

```python
from attune_author.manifest import match_files_to_features

changed = ["src/auth/login.py", "src/api/users.py"]
matches = match_files_to_features(changed, manifest)
print(matches)
```

Expected output:
```
{'auth': ['src/auth/login.py'], 'api': ['src/api/users.py']}
```

**Next:** Create your own features.yaml manifest using `save_manifest()` to organize your project's features.
