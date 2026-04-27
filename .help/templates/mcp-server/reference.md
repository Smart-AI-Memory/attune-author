---
type: reference
feature: mcp-server
depth: reference
generated_at: 2026-04-26T19:49:24.350905+00:00
source_hash: ac562ed08ae3ee05fce7d2be7da63d01dec77f2cc64ab8e75c6cd9b9ea9a676e
status: generated
---

# MCP server reference

Build MCP tool handlers and run the attune-author server for Claude Code integration.

## Classes

| Class | Description |
|-------|-------------|
| `AttuneAuthorHandlers` | Async handlers for the 6 attune-author MCP tools |
| `AttuneAuthorMCPServer` | MCP server for attune-author |

### AttuneAuthorHandlers

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `__init__` | `workspace_root: str` | `None` | Initialize handlers with workspace root |
| `author_init` | `args: dict[str, Any]` | `dict[str, Any]` | Bootstrap a .help/ directory in the project |
| `author_status` | `args: dict[str, Any]` | `dict[str, Any]` | Report which feature templates are stale |
| `author_generate` | `args: dict[str, Any]` | `dict[str, Any]` | Generate templates for a single feature |
| `author_maintain` | `args: dict[str, Any]` | `dict[str, Any]` | Regenerate all stale feature templates |
| `author_docs` | `args: dict[str, Any]` | `dict[str, Any]` | Generate documentation from a source file |
| `author_lookup` | `args: dict[str, Any]` | `dict[str, Any]` | Look up help for a topic by name or tag |

### AttuneAuthorMCPServer

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `__init__` | `workspace_root: str \| None = None` | `None` | Initialize MCP server |
| `call_tool` | `tool_name: str, arguments: dict[str, Any]` | `dict[str, Any]` | Execute a tool by name with arguments |

| Property | Type | Description |
|----------|------|-------------|
| `tools` | `dict[str, dict[str, Any]]` | Tool schema registry |

## Functions

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `validate_file_path` | `path: str, allowed_dir: str \| None = None` | `Path` | Validate a user-controlled file path |
| `create_server` | | `AttuneAuthorMCPServer` | Create and return a fresh AttuneAuthorMCPServer |
| `main` | | `None` | Entry point for the attune-author MCP server |
| `get_tools` | | `dict[str, dict[str, Any]]` | Return all attune-author MCP tool definitions |

### validate_file_path

| Raises | Message |
|--------|---------|
| `ValueError` | `'path must be a non-empty string'` |
| `ValueError` | `'path contains null bytes'` |
| `ValueError` | `'Path is outside the project: {...} is a system directory'` |
| `ValueError` | `'Invalid path: {...}'` |
| `ValueError` | `"Path '{...}' is outside allowed directory '{...}'"` |

## Tool schema definitions

The `get_tools()` function returns schema definitions for six MCP tools:

### author_init

| Field | Value |
|-------|-------|
| `description` | Bootstrap a .help/ directory in the project. Scans for features and creates features.yaml with discovered modules. Use when setting up a help system for the first time. |

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `project_root` | `string` | `'.'` | Project root directory (default: cwd). |

### author_status

| Field | Value |
|-------|-------|
| `description` | Report which feature templates are stale by comparing source file hashes against template frontmatter. Returns markdown with stale and current feature lists. |

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `help_dir` | `string` | `'.help'` | Path to .help/ directory. |
| `project_root` | `string` | `'.'` | Project root directory. |

### author_generate

| Field | Value |
|-------|-------|
| `description` | Generate concept, task, and reference templates for a single feature. Uses Jinja2 meta templates and optional LLM polish if ANTHROPIC_API_KEY is set. |

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `feature` | `string` | | ✓ | Feature name from features.yaml. |
| `help_dir` | `string` | `'.help'` | | Path to .help/ directory. |
| `project_root` | `string` | `'.'` | | Project root directory. |
| `overwrite` | `boolean` | `False` | | Overwrite manual templates. |

### author_maintain

| Field | Value |
|-------|-------|
| `description` | Detect and regenerate all stale feature templates in one pass. Useful after large refactors or before a release. Use dry_run=true to preview without writing files. |

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `help_dir` | `string` | `'.help'` | Path to .help/ directory. |
| `project_root` | `string` | `'.'` | Project root directory. |
| `features` | `array` | | Optional subset of feature names. |
| `dry_run` | `boolean` | `False` | Report stale features without regenerating. |

### author_docs

| Field | Value |
|-------|-------|
| `description` | Generate documentation from a source file using the 3-stage pipeline (outline -> write -> review). Requires ANTHROPIC_API_KEY. Use for API references, guides, or README sections. |

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `target` | `string` | | ✓ | Source file path or raw content. |
| `doc_type` | `string` | `'api-reference'` | | Documentation type (api-reference, guide, readme). |
| `audience` | `string` | `'developers'` | | Target audience. |
| `output_path` | `string` | | | Optional path to write the result. |

### author_lookup

| Field | Value |
|-------|-------|
| `description` | Look up help for a topic by name or tag. Resolves the query against features.yaml and returns the concept, task, or reference template content. |

| Parameter | Type | Values | Default | Required | Description |
|-----------|------|--------|---------|----------|-------------|
| `query` | `string` | | | ✓ | Topic to look up (feature name, tag, or substring). |
| `depth` | `string` | `'concept'`, `'task'`, `'reference'` | `'concept'` | | Template depth. |
| `help_dir` | `string` | | `'.help'` | | Path to .help/ directory. |

## Constants

| Constant | Values | Description |
|----------|--------|-------------|
| `_DANGEROUS_PREFIXES` | `'/etc'`, `'/sys'`, `'/proc'`, `'/dev'`, `'/boot'`, `'/root'`, `'/usr/sbin'`, `'/usr/bin'`, `'/sbin'`, `'/bin'`, `'/private/etc'`, `'/private/sys'`, `'/private/proc'`, `'/private/dev'`, `'/private/boot'`, `'/private/root'` | System directories blocked by path validation |
