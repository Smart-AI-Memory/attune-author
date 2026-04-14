---
type: quickstart
feature: bootstrap
depth: quickstart
generated_at: 2026-04-14T14:04:38.779070+00:00
source_hash: 747d4d8b3e41bb5a6d7a534fb1402fcfcda15486e7b1994427f88a2f71907ebf
status: generated
---

# Quickstart: bootstrap

```python
from attune_author.bootstrap import scan_project

proposals = scan_project(".")
for proposal in proposals:
    print(f"{proposal.name}: {proposal.description}")
```

## Prerequisites

- Python environment with attune_author installed
- A project directory to scan (can be your current project)

## Steps

1. **Scan your project** to discover potential features:

   ```python
   from attune_author.bootstrap import scan_project

   proposals = scan_project(".")
   ```

2. **Review the discovered features**:

   ```python
   for proposal in proposals:
       print(f"Found: {proposal.name}")
       print(f"  Description: {proposal.description}")
       print(f"  Files: {proposal.files}")
       print(f"  Confidence: {proposal.confidence}")
       print()
   ```

3. **Convert approved proposals to a manifest**:

   ```python
   from attune_author.bootstrap import proposals_to_manifest

   # Filter or modify proposals as needed
   selected_proposals = [p for p in proposals if p.confidence in ['high', 'medium']]

   manifest = proposals_to_manifest(selected_proposals)
   ```

## Expected output

The scanner identifies common patterns like entry points (`main.py`, `app.py`), configuration files, and package structures. You'll see output like:

```
Found: main_module
  Description: Primary application entry point
  Files: ['src/myapp/main.py']
  Confidence: high

Found: config_handler
  Description: Configuration management module
  Files: ['src/myapp/config.py', 'config/settings.py']
  Confidence: medium
```

**Next:** Use the generated manifest to create documentation templates for your discovered features.
