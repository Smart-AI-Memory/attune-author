---
type: reference
feature: mcp-server
depth: reference
generated_at: 2026-04-12T04:52:43.304733+00:00
source_hash: ede5ab36c4a3cf2b73e64330e50a7c9cd90cbe45b9b8d5be3909ee9d4c036883
status: generated
---

# MCP server reference

## Classes

| Class | Description |
|-------|-------------|
| `AttuneAuthorMCPServer` | MCP server that exposes attune-author functionality through the Model Context Protocol |
| `AttuneAuthorHandlers` | Async handlers for the 6 attune-author MCP tools |

### AttuneAuthorMCPServer methods

| Method | Parameters | Description |
|--------|------------|-------------|
| `__init__` | `workspace_root: str \| None = None` | Initialize the MCP server with optional workspace root directory |
| `tools` | None | Return dictionary of available MCP tool definitions |
| `call_tool` | `tool_name: str, arguments: dict[str, Any]` | Execute a named tool with provided arguments |

### AttuneAuthorHandlers methods

| Method | Parameters | Description |
|--------|------------|-------------|
| `__init__` | `workspace_root: str` | Initialize handlers with workspace root directory |
| `author_init` | `args: dict[str, Any]` | Initialize a new documentation workspace |
| `author_status` | `args: dict[str, Any]` | Get current workspace status and configuration |
| `author_generate` | `args: dict[str, Any]` | Generate documentation from source code |
| `author_maintain` | `args: dict[str, Any]` | Update and maintain existing documentation |
| `author_docs` | `args: dict[str, Any]` | Access and manipulate documentation files |
| `author_lookup` | `args: dict[str, Any]` | Search and retrieve documentation content |

## Functions

| Function | Parameters | Return Type | Description |
|----------|------------|-------------|-------------|
| `create_server` | None | `AttuneAuthorMCPServer` | Create and return a fresh AttuneAuthorMCPServer instance |
| `main` | None | `None` | Entry point for the attune-author MCP server |
| `get_tools` | None | `dict[str, dict[str, Any]]` | Return all attune-author MCP tool schema definitions |
| `validate_file_path` | `path: str, allowed_dir: str \| None = None` | `Path` | Validate and sanitize user-provided file paths |

## Source files

- `src/attune_author/mcp/server.py` — MCP server implementation
- `src/attune_author/mcp/handlers.py` — Tool request handlers
- `src/attune_author/mcp/tool_schemas.py` — Tool schema definitions
- `src/attune_author/mcp/path_validation.py` — Path validation utilities

## Tags

`mcp`, `integration`, `claude-code`
