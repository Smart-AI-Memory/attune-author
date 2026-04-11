---
type: faq
feature: bootstrap
depth: faq
generated_at: 2026-04-11T04:52:32.897422+00:00
source_hash: ba3e45edbaf44fba671f221a61e39cae7381b0b1c8ce9a02129f76b20bc6f331
status: generated
---

# Bootstrap FAQ

## What is bootstrap?

Bootstrap scans your project directory and proposes an initial feature manifest based on your project's structure and Python package layout.

## When should I use bootstrap?

Use bootstrap when you're setting up a new project and want to automatically generate a feature manifest. It's most helpful when you have an existing Python project structure but haven't created a `.help/features.yaml` file yet.

## How do I scan a project for features?

Call `scan_project()` with your project root directory. It returns a list of `ProposedFeature` objects that you can review and accept:

```python
from attune_author.bootstrap import scan_project
proposals = scan_project("/path/to/your/project")
```

## How do I convert proposals into a manifest?

Use `proposals_to_manifest()` to convert your accepted proposals into a `FeatureManifest`:

```python
from attune_author.bootstrap import proposals_to_manifest
manifest = proposals_to_manifest(accepted_proposals)
```

## How do I debug bootstrap issues?

First, run the tests: `pytest -k "bootstrap" -v`. If they pass but your code fails, add `logger.debug` statements at suspected failure points and re-run with logging enabled.

## Where are the source files?

- `src/attune_author/bootstrap.py`

**Tags:** `setup`, `scanning`, `manifest`
