---
type: reference
feature: mcp-server
depth: reference
generated_at: 2026-04-14T14:10:47.364042+00:00
source_hash: 05e470fa9511d5f688563c951fcd05ded9d16bcb0a768159c902d303a6418936
status: generated
---

# MCP server reference

## Classes

### AttuneAuthorMCPServer

MCP server for attune-author.

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `__init__` | `workspace_root: str \| None = None` | `None` | Initialize MCP server |
| `call_tool` | `tool_name: str, arguments: dict[str, Any]` | `dict[str, Any]` | Execute MCP tool by name |

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `tools` | `dict[str, dict[str, Any]]` | Tool schema registry |

### AttuneAuthorHandlers

Async handlers for the 6 attune-author MCP tools.

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `__init__` | `workspace_root: str` | `None` | Initialize handlers |
| `author_init` | `args: dict[str, Any]` | `dict[str, Any]` | Bootstrap .help/ directory |
| `author_status` | `args: dict[str, Any]` | `dict[str, Any]` | Report stale templates |
| `author_generate` | `args: dict[str, Any]` | `dict[str, Any]` | Generate feature templates |
| `author_maintain` | `args: dict[str, Any]` | `dict[str, Any]` | Regenerate stale templates |
| `author_docs` | `args: dict[str, Any]` | `dict[str, Any]` | Generate documentation |
| `author_lookup` | `args: dict[str, Any]` | `dict[str, Any]` | Look up help topics |

## Functions

| Function | Parameters | Returns | Description | Raises |
|----------|------------|---------|-------------|--------|
| `create_server` | none | `AttuneAuthorMCPServer` | Create and return a fresh AttuneAuthorMCPServer | |
| `main` | none | `None` | Entry point for the attune-author MCP server | |
| `get_tools` | none | `dict[str, dict[str, Any]]` | Return all attune-author MCP tool definitions | |
| `validate_file_path` | `path: str, allowed_dir: str \| None = None` | `Path` | Validate a user-controlled file path | `ValueError` |

### validate_file_path exceptions

| Exception | Message |
|-----------|---------|
| `ValueError` | `'path must be a non-empty string'` |
| `ValueError` | `'path contains null bytes'` |
| `ValueError` | `'Path is outside the project: {...} is a system directory'` |
| `ValueError` | `'Invalid path: {...}'` |
| `ValueError` | `"Path '{...}' is outside allowed directory '{...}'"` |

## Tool definitions

### author_init

Bootstrap a .help/ directory in the project. Scans for features and creates features.yaml with discovered modules. Use when setting up a help system for the first time.

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `project_root` | `string` | `'.'` | No | Project root directory (default: cwd) |

### author_status

Report which feature templates are stale by comparing source file hashes against template frontmatter. Returns markdown with stale and current feature lists.

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `help_dir` | `string` | `'.help'` | No | Path to .help/ directory |
| `project_root` | `string` | `'.'` | No | Project root directory |

### author_generate

Generate concept, task, and reference templates for a single feature. Uses Jinja2 meta templates and optional LLM polish if ANTHROPIC_API_KEY is set.

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `feature` | `string` | none | Yes | Feature name from features.yaml |
| `help_dir` | `string` | `'.help'` | No | Path to .help/ directory |
| `project_root` | `string` | `'.'` | No | Project root directory |
| `overwrite` | `boolean` | `False` | No | Overwrite manual templates |

### author_maintain

Detect and regenerate all stale feature templates in one pass. Useful after large refactors or before a release. Use dry_run=true to preview without writing files.

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `help_dir` | `string` | `'.help'` | No | Path to .help/ directory |
| `project_root` | `string` | `'.'` | No | Project root directory |
| `features` | `array` of `string` | none | No | Optional subset of feature names |
| `dry_run` | `boolean` | `False` | No | Report stale features without regenerating |

### author_docs

Generate documentation from a source file using the 3-stage pipeline (outline -> write -> review). Requires ANTHROPIC_API_KEY. Use for API references, guides, or README sections.

| Parameter | Type | Default | Required | Allowed values | Description |
|-----------|------|---------|----------|----------------|-------------|
| `target` | `string` | none | Yes | | Source file path or raw content |
| `doc_type` | `string` | `'api-reference'` | No | | Documentation type (api-reference, guide, readme) |
| `audience` | `string` | `'developers'` | No | | Target audience |
| `output_path` | `string` | none | No | | Optional path to write the result |

### author_lookup

Look up help for a topic by name or tag. Resolves the query against features.yaml and returns the concept, task, or reference template content.

| Parameter | Type | Default | Required | Allowed values | Description |
|-----------|------|---------|----------|----------------|-------------|
| `query` | `string` | none | Yes | | Topic to look up (feature name, tag, or substring) |
| `depth` | `string` | `'concept'` | No | `concept`, `task`, `reference` | Template depth |
| `help_dir` | `string` | `'.help'` | No | | Path to .help/ directory |

## Constants

### Dangerous prefixes

| Constant | Values |
|----------|--------|
| `_DANGEROUS_PREFIXES` | `/etc`, `/sys`, `/proc`, `/dev`, `/boot`, `/root`, `/usr/sbin`, `/usr/bin`, `/sbin`, `/bin`, `/private/etc`, `/private/sys`, `/private/proc`, `/private/dev`, `/private/boot`, `/private/root` |
