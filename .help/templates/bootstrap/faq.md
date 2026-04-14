---
type: faq
feature: bootstrap
depth: faq
generated_at: 2026-04-14T16:09:22.133266+00:00
source_hash: 747d4d8b3e41bb5a6d7a534fb1402fcfcda15486e7b1994427f88a2f71907ebf
status: generated
---

# Bootstrap FAQ

## What is the bootstrap feature?

Bootstrap scans your project directory to automatically discover features and generate an initial feature manifest based on your codebase structure.

## When should I use bootstrap?

Use bootstrap when you're starting fresh with a new project or want to regenerate your feature manifest from scratch. It's particularly useful for onboarding existing codebases that don't yet have documentation tooling set up.

## How do I scan a project for features?

Call `scan_project()` with your project's root directory. It returns a list of `ProposedFeature` objects that represent discovered functionality:

```python
from attune_author.bootstrap import scan_project
proposals = scan_project("/path/to/your/project")
```

## How do I turn proposals into a manifest?

Use `proposals_to_manifest()` to convert your selected proposals into a `FeatureManifest`:

```python
from attune_author.bootstrap import proposals_to_manifest
manifest = proposals_to_manifest(selected_proposals)
```

## What does a ProposedFeature contain?

Each `ProposedFeature` has:
- `name`: The feature's identifier
- `description`: What the feature does
- `files`: Source files associated with this feature
- `tags`: Classification tags
- `confidence`: How certain the scanner is about this feature
- `reason`: Why this was identified as a feature

## What directories does bootstrap skip?

Bootstrap ignores common build artifacts and tool directories like `.git`, `__pycache__`, `.venv`, `node_modules`, and `dist`. You don't need to clean these up before scanning.

## How do I debug bootstrap issues?

Run `pytest -k "bootstrap" -v` to check if the core functionality works. If scanning fails on your specific project, add debug logging to see which files or directories are causing problems.

## Where is the bootstrap code?

All bootstrap functionality is in `src/attune_author/bootstrap.py`.

**Tags:** `setup`, `scanning`, `manifest`
