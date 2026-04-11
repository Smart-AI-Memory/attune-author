---
type: reference
feature: mcp-server
depth: reference
generated_at: 2026-04-11T04:58:31.944288+00:00
source_hash: d99e670e0306a6da8972a9bf7c1b94a808c3f1fb3c17fad5dee28bdc1183bac4
status: generated
---

# MCP Server reference

## Classes

| Class | Description |
|-------|-------------|
| `AttuneAuthorMCPServer` | MCP server implementation for attune-author with tool registration and execution capabilities |
| `AttuneAuthorHandlers` | Asynchronous handlers for six attune-author MCP tools |

### AttuneAuthorMCPServer methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `(workspace_root: str \| None = None) -> None` | Initialize server with optional workspace root directory |
| `tools` | `() -> dict[str, dict[str, Any]]` | Get all available tool definitions |
| `call_tool` | `(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]` | Execute a tool with provided arguments |

### AttuneAuthorHandlers methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `(workspace_root: str) -> None` | Initialize handlers with workspace root directory |
| `author_init` | `(args: dict[str, Any]) -> dict[str, Any]` | Initialize new authoring project |
| `author_status` | `(args: dict[str, Any]) -> dict[str, Any]` | Check project status |
| `author_generate` | `(args: dict[str, Any]) -> dict[str, Any]` | Generate documentation content |
| `author_maintain` | `(args: dict[str, Any]) -> dict[str, Any]` | Maintain existing documentation |
| `author_docs` | `(args: dict[str, Any]) -> dict[str, Any]` | Handle documentation operations |
| `author_lookup` | `(args: dict[str, Any]) -> dict[str, Any]` | Look up project information |

## Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `create_server` | `() -> AttuneAuthorMCPServer` | Create and return a fresh MCP server instance |
| `main` | `() -> None` | Entry point for the attune-author MCP server |
| `get_tools` | `() -> dict[str, dict[str, Any]]` | Return all attune-author MCP tool definitions |
| `validate_file_path` | `(path: str, allowed_dir: str \| None = None) -> Path` | Validate and sanitize user-provided file paths |

## Source files

- `src/attune_author/mcp/server.py` - MCP server implementation
- `src/attune_author/mcp/handlers.py` - MCP tool handlers
- `src/attune_author/mcp/tool_schemas.py` - MCP tool schema definitions
- `src/attune_author/mcp/path_validation.py` - Path validation utilities
