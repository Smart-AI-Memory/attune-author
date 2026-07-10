---
type: concept
name: bootstrap-concept
feature: bootstrap
depth: concept
generated_at: 2026-07-10T13:07:32.382854+00:00
source_hash: 40cd7c5eca29231d1a865aa04654239348b46aed8c204904aacc473fc810affe
status: generated
scaffold_hash: 86c6577f7fd5f4575d4b8c7ef0c1fb4ae3ef232e9436313a11797aea1ba12888
---

# Bootstrap

Bootstrap scans an existing project and proposes an initial feature manifest, so you don't have to write one from scratch. Instead of listing every feature by hand, you run a scan, review the proposals, and convert the ones you accept into a manifest.

## How it works

The scan-and-convert flow has two steps, each backed by one public function:

1. **`scan_project(project_root)`** walks the project's directory structure and Python package layout and returns a list of `ProposedFeature` objects — one per feature it thinks it found. The scanner skips noise directories such as `.git`, `__pycache__`, `.venv`, and `node_modules`, and it uses signals like entry-point filenames (for example `main.py`, `cli.py`, `server.py`) and configuration naming patterns (`config`, `settings`, `conf`) to decide what looks like a feature.
2. **`proposals_to_manifest(proposals)`** takes the proposals you've accepted and converts them into a `FeatureManifest`, the structure the rest of the system consumes.

Each `ProposedFeature` carries enough information for you to judge it before accepting:

| Field | What it tells you |
|---|---|
| `name` | The proposed feature name |
| `description` | What the scanner thinks the feature does |
| `files` | The source files grouped under this feature |
| `tags` | Searchable tags suggested for the feature |
| `confidence` | How sure the scanner is (defaults to `medium`) |
| `reason` | Why the scanner proposed this feature |

The `confidence` and `reason` fields exist because scanning is heuristic: the scanner explains its guesses so you can accept, edit, or discard each proposal rather than trusting the output blindly.

## What connects to it

Bootstrap sits at the front of the setup pipeline: it produces the manifest that scanning and generation later depend on. The rest of the codebase interacts with it through these interfaces:

| Interface | Purpose | File |
|-----------|---------|------|
| `scan_project` | Scan a project and propose features | `src/attune_author/bootstrap.py` |
| `proposals_to_manifest` | Convert accepted proposals to a `FeatureManifest` | `src/attune_author/bootstrap.py` |
| `ProposedFeature` | A feature discovered by scanning | `src/attune_author/bootstrap.py` |

A useful mental model: bootstrap is the one-time (or occasional) step that turns a raw project tree into structured proposals, and `FeatureManifest` is the handoff point where its job ends and the rest of the system takes over.
