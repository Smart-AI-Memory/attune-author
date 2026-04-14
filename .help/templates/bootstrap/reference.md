---
type: reference
feature: bootstrap
depth: reference
generated_at: 2026-04-14T14:03:39.709180+00:00
source_hash: 747d4d8b3e41bb5a6d7a534fb1402fcfcda15486e7b1994427f88a2f71907ebf
status: generated
---

# Bootstrap reference

## Classes

| Class | Description |
|-------|-------------|
| `ProposedFeature` | A feature discovered by scanning |

### ProposedFeature fields

| Field | Type | Default |
|-------|------|---------|
| `name` | `str` | (required) |
| `description` | `str` | (required) |
| `files` | `list[str]` | `[]` |
| `tags` | `list[str]` | `[]` |
| `confidence` | `str` | `'medium'` |
| `reason` | `str` | `''` |

## Functions

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `scan_project` | `project_root: str \| Path` | `list[ProposedFeature]` | Scan a project and propose features |
| `proposals_to_manifest` | `proposals: list[ProposedFeature]` | `FeatureManifest` | Convert accepted proposals to a FeatureManifest |

## Constants

| Constant | Values |
|----------|--------|
| `SKIP_DIRS` | `.git`, `.github`, `.help`, `.claude`, `.agents`, `__pycache__`, `.mypy_cache`, `.pytest_cache`, `.ruff_cache`, `.tox`, `.venv`, `venv`, `env`, `node_modules`, `dist`, `build`, `.egg-info`, `htmlcov`, `site` |
| `ENTRY_POINT_NAMES` | `main.py`, `app.py`, `cli.py`, `server.py`, `manage.py`, `wsgi.py`, `asgi.py`, `index.ts`, `index.js`, `main.go`, `main.rs` |
| `CONFIG_PATTERNS` | `config`, `settings`, `conf` |
