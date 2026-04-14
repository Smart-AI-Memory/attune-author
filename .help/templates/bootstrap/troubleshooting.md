---
type: troubleshooting
feature: bootstrap
depth: troubleshooting
generated_at: 2026-04-14T16:09:06.878517+00:00
source_hash: 747d4d8b3e41bb5a6d7a534fb1402fcfcda15486e7b1994427f88a2f71907ebf
status: generated
---

# Troubleshoot bootstrap

## Before you start

The bootstrap feature scans your project directory and proposes an initial feature manifest based on file structure and detected entry points. It analyzes Python packages, configuration files, and common project patterns to suggest features automatically.

## Symptom table

| If you observe | Check |
|----------------|-------|
| Empty or incomplete proposal list | Verify your project root contains recognizable files and isn't mostly in `_SKIP_DIRS` |
| Missing obvious features | Check if key files are in skipped directories or have unrecognized naming patterns |
| Incorrect confidence levels | Review the `reason` field in `ProposedFeature` objects for scoring logic |
| Scan takes too long | Look for symbolic links or deep directory nesting that bypasses skip filters |

## Step-by-step diagnosis

1. **Reproduce with minimal input.**
   Test `scan_project()` directly with your project root path. Print the returned `ProposedFeature` list to see what the scanner actually detects before any filtering or processing.

2. **Verify project structure assumptions.**
   Check that your project root is accessible and contains files outside the skip list. The scanner looks for entry points in `_ENTRY_POINT_NAMES` and config patterns in `_CONFIG_PATTERNS`.

3. **Examine individual proposals.**
   For each `ProposedFeature`, inspect the `files`, `tags`, and `confidence` fields. The `reason` field explains why the scanner assigned that confidence level.

4. **Test manifest conversion.**
   If scanning works but `proposals_to_manifest()` fails, pass your proposal list to the function separately to isolate whether the issue is in detection or conversion.

## Common fixes

- **Add missing entry points.** If your main application file isn't named `main.py`, `app.py`, `cli.py`, `server.py`, `manage.py`, `wsgi.py`, or `asgi.py`, the scanner may miss it. Rename or create a recognizable entry point.

- **Move files out of skip directories.** The scanner ignores `.git`, `__pycache__`, `.venv`, `node_modules`, and other directories in `_SKIP_DIRS`. Move important source files to scanned locations.

- **Check file permissions.** Ensure the scanner can read your project files. Run `ls -la` in your project root to verify file permissions and ownership.

- **Handle non-Python projects.** The scanner looks for Python patterns but also recognizes `index.ts`, `index.js`, `main.go`, and `main.rs`. For other languages, you may need to add recognizable entry points or config files.

## Source files

- `src/attune_author/bootstrap.py`

**Tags:** `setup`, `scanning`, `manifest`
