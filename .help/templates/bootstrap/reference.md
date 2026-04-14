---
type: reference
feature: bootstrap
depth: reference
generated_at: 2026-04-14T16:08:35.223900+00:00
source_hash: 747d4d8b3e41bb5a6d7a534fb1402fcfcda15486e7b1994427f88a2f71907ebf
status: generated
---

# Bootstrap reference

Scan projects and generate feature manifests from discovered code patterns.

## Classes

| Class | Description |
|-------|-------------|
| `ProposedFeature` | A feature discovered by scanning |

### ProposedFeature fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | `str` | | Feature name |
| `description` | `str` | | Human-readable description |
| `files` | `list[str]` | `[]` | Associated file paths |
| `tags` | `list[str]` | `[]` | Classification tags |
| `confidence` | `str` | `'medium'` | Detection confidence level |
| `reason` | `str` | `''` | Why this feature was proposed |

## Functions

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `scan_project` | `project_root: str \| Path` | `list[ProposedFeature]` | Scan a project and propose features |
| `proposals_to_manifest` | `proposals: list[ProposedFeature]` | `FeatureManifest` | Convert accepted proposals to a FeatureManifest |

## Constants

| Constant | Values | Description |
|----------|--------|-------------|
| `_SKIP_DIRS` | `'.git'`, `'.github'`, `'.help'`, `'.claude'`, `'.agents'`, `'__pycache__'`, `'.mypy_cache'`, `'.pytest_cache'`, `'.ruff_cache'`, `'.tox'`, `'.venv'`, `'venv'`, `'env'`, `'node_modules'`, `'dist'`, `'build'`, `'.egg-info'`, `'htmlcov'`, `'site'` | Directories to skip during scanning |
| `_ENTRY_POINT_NAMES` | `'main.py'`, `'app.py'`, `'cli.py'`, `'server.py'`, `'manage.py'`, `'wsgi.py'`, `'asgi.py'`, `'index.ts'`, `'index.js'`, `'main.go'`, `'main.rs'` | Common application entry point filenames |
| `_CONFIG_PATTERNS` | `'config'`, `'settings'`, `'conf'` | Filename patterns for configuration files |
