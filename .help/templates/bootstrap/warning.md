---
type: warning
feature: bootstrap
depth: warning
generated_at: 2026-04-14T14:03:54.908392+00:00
source_hash: 747d4d8b3e41bb5a6d7a534fb1402fcfcda15486e7b1994427f88a2f71907ebf
status: generated
---

# Bootstrap cautions

## What to watch for

The bootstrap module scans your project directory to automatically propose features for your manifest. While this saves setup time, the scanning process makes assumptions about your project structure that can lead to incorrect or incomplete feature detection.

## Risk areas

### Directory traversal limits

`scan_project()` skips common directories like `.git`, `__pycache__`, and `node_modules` using the hardcoded `_SKIP_DIRS` set. If your project stores important code in unconventionally named directories (like a `vendor` folder with custom modules), the scanner will ignore them completely.

### Entry point detection assumptions

The scanner looks for specific filenames (`main.py`, `app.py`, `cli.py`, etc.) defined in `_ENTRY_POINT_NAMES` to identify application entry points. Projects with non-standard entry point names or multiple entry points per feature may be mischaracterized or have features missed entirely.

### Configuration file pattern matching

`_CONFIG_PATTERNS` only recognizes files containing 'config', 'settings', or 'conf' in their names. Projects using different naming conventions (like `env.py`, `constants.py`, or `.toml` files) won't be properly categorized as configuration features.

### Confidence scoring opacity

`ProposedFeature` objects include a `confidence` field that defaults to 'medium', but the scanning logic that sets this value isn't exposed. Low-confidence proposals might indicate genuine uncertainty about a feature's purpose, requiring manual review before acceptance.

## How to avoid problems

1. **Verify scan results manually.** Always review the output of `scan_project()` before converting proposals to a manifest. Missing or misclassified features are easier to catch at this stage than after deployment.

2. **Customize for your project structure.** If your project uses non-standard directory names or entry points, consider extending the hardcoded sets or implementing custom scanning logic rather than relying on the defaults.

3. **Check confidence levels.** Pay special attention to proposals with low confidence scores or empty `reason` fields. These often indicate edge cases where the scanner couldn't determine a feature's purpose reliably.

4. **Test with representative projects.** Before using bootstrap on production codebases, test it against projects with similar structures to yours. Different languages, frameworks, or organizational patterns may not scan as expected.

## Source files

- `src/attune_author/bootstrap.py`

**Tags:** `setup`, `scanning`, `manifest`
