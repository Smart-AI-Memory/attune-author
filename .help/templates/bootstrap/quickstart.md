---
type: quickstart
feature: bootstrap
depth: quickstart
generated_at: 2026-04-11T04:52:42.034982+00:00
source_hash: ba3e45edbaf44fba671f221a61e39cae7381b0b1c8ce9a02129f76b20bc6f331
status: generated
---

# Quickstart: bootstrap

```python
from attune_author.bootstrap import scan_project, proposals_to_manifest

proposals = scan_project(".")
manifest = proposals_to_manifest(proposals)
print(manifest)
```

This scans your current directory and generates a feature manifest based on your project structure.

## Prerequisites

- The project is cloned and installed locally
- Access to the files under src/attune_author/bootstrap.py

## Create your first manifest

1. **Scan your project directory.** Run the scan to discover potential features:

```python
from attune_author.bootstrap import scan_project

proposals = scan_project("/path/to/your/project")
print(f"Found {len(proposals)} proposed features")
```

2. **Convert proposals to a manifest.** Transform the discovered features into a working manifest:

```python
from attune_author.bootstrap import proposals_to_manifest

manifest = proposals_to_manifest(proposals)
```

3. **Review the results.** Each `ProposedFeature` contains details about what the scanner found:

```python
for proposal in proposals:
    print(f"Feature: {proposal}")
```

Expected output shows discovered Python packages, configuration files, and project structure patterns that map to potential features.

## Next steps

Read the bootstrap concept page to understand how project scanning works and what patterns it recognizes.

## Source files

- `src/attune_author/bootstrap.py`

**Tags:** `setup`, `scanning`, `manifest`
