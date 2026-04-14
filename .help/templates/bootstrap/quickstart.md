---
type: quickstart
feature: bootstrap
depth: quickstart
generated_at: 2026-04-14T16:09:32.341254+00:00
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

This command scans your current project directory and discovers potential features based on file patterns and project structure.

## Prerequisites

- Python project with `attune_author` installed
- Project directory to scan (current directory works fine)

## Scan your project

1. **Scan for features** in your project root:
   ```python
   from attune_author.bootstrap import scan_project

   proposals = scan_project("/path/to/your/project")
   ```

2. **Review the discovered features**:
   ```python
   for proposal in proposals:
       print(f"Feature: {proposal.name}")
       print(f"Description: {proposal.description}")
       print(f"Files: {proposal.files}")
       print(f"Confidence: {proposal.confidence}")
       print("---")
   ```

3. **Convert proposals to a manifest**:
   ```python
   from attune_author.bootstrap import proposals_to_manifest

   manifest = proposals_to_manifest(proposals)
   ```

## Expected output

```
Feature: cli
Description: Command-line interface module
Files: ['cli.py', 'main.py']
Confidence: high
---
Feature: config
Description: Configuration management
Files: ['config.py', 'settings.py']
Confidence: medium
---
```

**Next:** Save your manifest to start documenting the discovered features.
