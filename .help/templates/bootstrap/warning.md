---
type: warning
feature: bootstrap
depth: warning
generated_at: 2026-04-11T04:52:06.195677+00:00
source_hash: ba3e45edbaf44fba671f221a61e39cae7381b0b1c8ce9a02129f76b20bc6f331
status: generated
---

# Bootstrap cautions

## What to watch for

The bootstrap feature scans your project directory to propose an initial feature manifest. While convenient for getting started, this automated scanning can misinterpret your project structure and create unexpected configurations.

## Risk areas

**Project structure misinterpretation**
`scan_project()` makes assumptions about your directory layout that may not match your project's conventions. It can mistake test directories for feature modules, overlook custom package structures, or incorrectly categorize files based on naming patterns.

**Incomplete feature detection**
The scanner only recognizes common Python patterns. If your project uses unconventional organization, custom build systems, or mixed-language components, `scan_project()` may miss important features or create incomplete proposals.

**Manifest generation overwrites**
`proposals_to_manifest()` converts scan results into a concrete manifest structure. If you run this on an existing project with manual configuration, it may overwrite carefully crafted settings with generic defaults.

## How to avoid problems

1. **Review proposals before committing.** Always inspect the `ProposedFeature` objects from `scan_project()` before passing them to `proposals_to_manifest()`. Verify that detected features match your intended project structure.

2. **Start with a clean slate.** Bootstrap works best on new projects or when you want to completely rebuild your feature configuration. For existing projects with custom setups, consider manual configuration instead.

3. **Test the generated manifest.** After running `proposals_to_manifest()`, validate the resulting `FeatureManifest` against your project's actual behavior before saving it to disk.

4. **Use selective acceptance.** You don't have to accept all proposals. Filter the list from `scan_project()` to include only the features you want before generating the final manifest.

## Source files

- `src/attune_author/bootstrap.py`

**Tags:** `setup`, `scanning`, `manifest`
