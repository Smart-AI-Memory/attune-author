---
type: faq
feature: bootstrap
depth: faq
generated_at: 2026-04-14T14:04:26.984748+00:00
source_hash: 747d4d8b3e41bb5a6d7a534fb1402fcfcda15486e7b1994427f88a2f71907ebf
status: generated
---

# Bootstrap FAQ

## What is bootstrap?

Bootstrap scans your project directory to automatically propose features for your manifest based on the files and structure it finds.

## When should I use bootstrap?

Use bootstrap when you're starting with a new project or want to regenerate your feature manifest. It's especially helpful if you have an existing codebase without documentation and want to quickly identify the key components.

## What's the main entry point?

Start with `scan_project()` to analyze your project structure and get a list of proposed features. Then use `proposals_to_manifest()` to convert the ones you want into a proper FeatureManifest.

Both functions are in `src/attune_author/bootstrap.py`.

## What does scan_project() look for?

The scanner identifies potential features by looking for:

- Entry point files like `main.py`, `app.py`, `cli.py`, `server.py`
- Configuration-related files containing patterns like "config", "settings", or "conf"
- Python packages and modules in your project structure

It skips common build and cache directories like `.git`, `__pycache__`, `node_modules`, and virtual environments.

## What information does each proposed feature include?

Each `ProposedFeature` contains:
- A name and description
- The files associated with that feature
- Tags for categorization
- A confidence level (defaults to "medium")
- The reasoning behind why it was proposed

## How do I debug scanning issues?

Run `pytest -k "bootstrap" -v` to check the tests first. If scanning isn't finding features you expect, check that your files aren't in the skip list and that they match the entry point or config patterns the scanner looks for.

## Where are the source files?

- `src/attune_author/bootstrap.py`

**Tags:** `setup`, `scanning`, `manifest`
