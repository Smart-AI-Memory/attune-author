---
type: reference
name: mcp-server-reference
feature: mcp-server
depth: reference
generated_at: 2026-07-10T13:10:16.627432+00:00
source_hash: 519bea9e9c202c9092219aeceb980f51775180a16ce6722ad9da40084799bf21
status: generated
scaffold_hash: 831bd1f59c0d3674050f6b6a907061a87e8f57a8dd2b9d2466ca8bc9c42a7abe
---

# MCP server reference

Expose attune-author's capabilities to Claude Code as six callable MCP tools. Use this reference to look up the server and handler classes, the path validation function and its error messages, and the exact input schema for each tool.

## Classes

| Class | Description | File |
|-------|-------------|------|
| `AttuneAuthorHandlers` | Async handlers for the 6 attune-author MCP tools. | `src/attune_author/mcp/handlers.py` |
| `AttuneAuthorMCPServer` | MCP server for attune-author. | `src/attune_author/mcp/server.py` |

### AttuneAuthorHandlers

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `__init__` | `workspace_root: str` | `None` | Initialize handlers rooted at a workspace directory. |
| `author_init` | `args: dict[str, Any]` | `dict[str, Any]` | Handle the `author_init` tool call. |
| `author_status` | `args: dict[str, Any]` | `dict[str, Any]` | Handle the `author_status` tool call. |
| `author_generate` | `args: dict[str, Any]` | `dict[str, Any]` | Handle the `author_generate` tool call. |
| `author_maintain` | `args: dict[str, Any]` | `dict[str, Any]` | Handle the `author_maintain` tool call. |
| `author_docs` | `args: dict[str, Any]` | `dict[str, Any]` | Handle the `author_docs` tool call. |
| `author_lookup` | `args: dict[str, Any]` | `dict[str, Any]` | Handle the `author_lookup` tool call. |

### AttuneAuthorMCPServer

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `__init__` | `workspace_root: str \| None = None` | `None` | Initialize the server, defaulting to the current workspace. |
| `call_tool` | `tool_name: str, arguments: dict[str, Any]` | `dict[str, Any]` | Dispatch a tool call by name with the given arguments. |

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `tools` | `dict[str, dict[str, Any]]` | Tool schema registry. |

## Functions

| Function | Parameters | Returns | Description | File |
|----------|------------|---------|-------------|------|
| `validate_file_path` | `path: str, allowed_dir: str \| None = None` | `Path` | Validate a user-controlled file path. | `src/attune_author/mcp/path_validation.py` |
| `create_server` | — | `AttuneAuthorMCPServer` | Create and return a fresh AttuneAuthorMCPServer. | `src/attune_author/mcp/server.py` |
| `main` | — | `None` | Entry point for the attune-author MCP server. | `src/attune_author/mcp/server.py` |
| `get_tools` | — | `dict[str, dict[str, Any]]` | Return all attune-author MCP tool definitions. | `src/attune_author/mcp/tool_schemas.py` |

### Raises

`validate_file_path` raises the following (`{...}` marks interpolated values):

| Exception | Message |
|-----------|---------|
| `ValueError` | `path must be a non-empty string` |
| `ValueError` | `path contains null bytes` |
| `ValueError` | `Path is outside the project: {...} is a system directory` |
| `ValueError` | `Invalid path: {...}` |
| `ValueError` | `Path '{...}' is outside allowed directory '{...}'` |

## Tool definitions

`get_tools()` returns the following six tool schemas.

### author_init

Bootstrap a `.help/` directory in the project. Scans for features and creates `features.yaml` with discovered modules. Use when setting up a help system for the first time.

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `project_root` | `string` | `'.'` | No | Project root directory (default: cwd). |

### author_status

Report which feature templates are stale by comparing source file hashes against template frontmatter. Returns markdown with stale and current feature lists.

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `help_dir` | `string` | `'.help'` | No | Path to `.help/` directory. |
| `project_root` | `string` | `'.'` | No | Project root directory. |

### author_generate

Generate concept, task, and reference templates for a single feature. Uses Jinja2 meta templates and optional LLM polish if `ANTHROPIC_API_KEY` is set.

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `feature` | `string` | — | Yes | Feature name from `features.yaml`. |
| `help_dir` | `string` | `'.help'` | No | Path to `.help/` directory. |
| `project_root` | `string` | `'.'` | No | Project root directory. |
| `overwrite` | `boolean` | `False` | No | Overwrite manual templates. |

### author_maintain

Detect and regenerate all stale feature templates in one pass. Useful after large refactors or before a release. Use `dry_run=true` to preview without writing files.

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `help_dir` | `string` | `'.help'` | No | Path to `.help/` directory. |
| `project_root` | `string` | `'.'` | No | Project root directory. |
| `features` | `array` of `string` | — | No | Optional subset of feature names. |
| `dry_run` | `boolean` | `False` | No | Report stale features without regenerating. |

### author_docs

Generate documentation from a source file using the 3-stage pipeline (outline -> write -> review). Requires `ANTHROPIC_API_KEY`. Use for API references, guides, or README sections.

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `target` | `string` | — | Yes | Source file path or raw content. |
| `doc_type` | `string` | `'api-reference'` | No | Documentation type (api-reference, guide, readme). |
| `audience` | `string` | `'developers'` | No | Target audience. |
| `output_path` | `string` | — | No | Optional path to write the result. |

### author_lookup

Look up help for a topic by name or tag. Resolves the query against `features.yaml` and returns the concept, task, or reference template content.

| Parameter | Type | Values | Default | Required | Description |
|-----------|------|--------|---------|----------|-------------|
| `query` | `string` | — | — | Yes | Topic to look up (feature name, tag, or substring). |
| `depth` | `string` | `'concept'`, `'task'`, `'reference'` | `'concept'` | No | Template depth. |
| `help_dir` | `string` | — | `'.help'` | No | Path to `.help/` directory. |

## Constants

| Constant | Values | Description |
|----------|--------|-------------|
| `_DANGEROUS_PREFIXES` | `'/etc'`, `'/sys'`, `'/proc'`, `'/dev'`, `'/boot'`, `'/root'`, `'/usr/sbin'`, `'/usr/bin'`, `'/sbin'`, `'/bin'`, `'/private/etc'`, `'/private/sys'`, `'/private/proc'`, `'/private/dev'`, `'/private/boot'`, `'/private/root'` | System directory prefixes that `validate_file_path` rejects. |

## Source files

- `src/attune_author/mcp/server.py`
- `src/attune_author/mcp/handlers.py`
- `src/attune_author/mcp/tool_schemas.py`
- `src/attune_author/mcp/path_validation.py`

## Tags

`mcp`, `integration`, `claude-code`
