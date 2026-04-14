---
type: reference
feature: mcp-server
depth: reference
generated_at: 2026-04-14T16:15:46.624718+00:00
source_hash: 05e470fa9511d5f688563c951fcd05ded9d16bcb0a768159c902d303a6418936
status: generated
---

# MCP server reference

Connect attune-author to Model Context Protocol (MCP) clients like Claude Desktop. Provides tool handlers for bootstrapping help systems, generating templates, and maintaining documentation.

## Classes

| Class | Description |
|-------|-------------|
| `AttuneAuthorMCPServer` | MCP server that exposes attune-author tools to MCP clients |
| `AttuneAuthorHandlers` | Async tool handlers for the six attune-author MCP operations |

### AttuneAuthorMCPServer

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `__init__` | `workspace_root: str \| None = None` | `None` | Initialize server with optional workspace root directory |
| `call_tool` | `tool_name: str, arguments: dict[str, Any]` | `dict[str, Any]` | Execute an MCP tool by name with the given arguments |

| Property | Type | Description |
|----------|------|-------------|
| `tools` | `dict[str, dict[str, Any]]` | Tool schema registry for all available MCP tools |

### AttuneAuthorHandlers

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `__init__` | `workspace_root: str` | `None` | Initialize handlers with workspace root directory |
| `author_init` | `args: dict[str, Any]` | `dict[str, Any]` | Bootstrap a .help/ directory and scan for features |
| `author_status` | `args: dict[str, Any]` | `dict[str, Any]` | Report which feature templates are stale |
| `author_generate` | `args: dict[str, Any]` | `dict[str, Any]` | Generate templates for a single feature |
| `author_maintain` | `args: dict[str, Any]` | `dict[str, Any]` | Regenerate all stale feature templates |
| `author_docs` | `args: dict[str, Any]` | `dict[str, Any]` | Generate documentation using the 3-stage pipeline |
| `author_lookup` | `args: dict[str, Any]` | `dict[str, Any]` | Look up help content by topic name or tag |

## Functions

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `create_server` | | `AttuneAuthorMCPServer` | Create and return a fresh AttuneAuthorMCPServer |
| `main` | | `None` | Entry point for the attune-author MCP server |
| `get_tools` | | `dict[str, dict[str, Any]]` | Return all attune-author MCP tool definitions |
| `validate_file_path` | `path: str, allowed_dir: str \| None = None` | `Path` | Validate a user-controlled file path |

### validate_file_path

| Exception | Message |
|-----------|---------|
| `ValueError` | `'path must be a non-empty string'` |
| `ValueError` | `'path contains null bytes'` |
| `ValueError` | `'Path is outside the project: {...} is a system directory'` |
| `ValueError` | `'Invalid path: {...}'` |
| `ValueError` | `"Path '{...}' is outside allowed directory '{...}'"` |

## Tool schemas

The `get_tools()` function returns schema definitions for six MCP tools:

### author_init

Bootstrap a .help/ directory in the project. Scans for features and creates features.yaml with discovered modules. Use when setting up a help system for the first time.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `project_root` | `string` | `'.'` | Project root directory (default: cwd) |

### author_status

Report which feature templates are stale by comparing source file hashes against template frontmatter. Returns markdown with stale and current feature lists.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `help_dir` | `string` | `'.help'` | Path to .help/ directory |
| `project_root` | `string` | `'.'` | Project root directory |

### author_generate

Generate concept, task, and reference templates for a single feature. Uses Jinja2 meta templates and optional LLM polish if ANTHROPIC_API_KEY is set.

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `feature` | `string` | | ✓ | Feature name from features.yaml |
| `help_dir` | `string` | `'.help'` | | Path to .help/ directory |
| `project_root` | `string` | `'.'` | | Project root directory |
| `overwrite` | `boolean` | `False` | | Overwrite manual templates |

### author_maintain

Detect and regenerate all stale feature templates in one pass. Useful after large refactors or before a release. Use dry_run=true to preview without writing files.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `help_dir` | `string` | `'.help'` | Path to .help/ directory |
| `project_root` | `string` | `'.'` | Project root directory |
| `features` | `array` | | Optional subset of feature names |
| `dry_run` | `boolean` | `False` | Report stale features without regenerating |

### author_docs

Generate documentation from a source file using the 3-stage pipeline (outline -> write -> review). Requires ANTHROPIC_API_KEY. Use for API references, guides, or README sections.

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `target` | `string` | | ✓ | Source file path or raw content |
| `doc_type` | `string` | `'api-reference'` | | Documentation type (api-reference, guide, readme) |
| `audience` | `string` | `'developers'` | | Target audience |
| `output_path` | `string` | | | Optional path to write the result |

### author_lookup

Look up help for a topic by name or tag. Resolves the query against features.yaml and returns the concept, task, or reference template content.

| Parameter | Type | Values | Default | Required | Description |
|-----------|------|--------|---------|----------|-------------|
| `query` | `string` | | | ✓ | Topic to look up (feature name, tag, or substring) |
| `depth` | `string` | `'concept'`, `'task'`, `'reference'` | `'concept'` | | Template depth |
| `help_dir` | `string` | | `'.help'` | | Path to .help/ directory |

## Constants

| Constant | Values | Description |
|----------|--------|-------------|
| `_DANGEROUS_PREFIXES` | `'/etc'`, `'/sys'`, `'/proc'`, `'/dev'`, `'/boot'`, `'/root'`, `'/usr/sbin'`, `'/usr/bin'`, `'/sbin'`, `'/bin'`, `'/private/etc'`, `'/private/sys'`, `'/private/proc'`, `'/private/dev'`, `'/private/boot'`, `'/private/root'` | System directories blocked by path validation |
