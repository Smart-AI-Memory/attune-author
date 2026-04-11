---
type: note
feature: mcp-server
depth: note
generated_at: 2026-04-11T04:59:48.085457+00:00
source_hash: d99e670e0306a6da8972a9bf7c1b94a808c3f1fb3c17fad5dee28bdc1183bac4
status: generated
---

# Note: mcp server

## Context

The Model Context Protocol (MCP) server exposes attune-author's capabilities as callable tools that Claude Code and other MCP clients can invoke remotely.

## Content

The MCP server implementation centers around two main classes:

- `AttuneAuthorMCPServer` - The primary server class that handles tool registration and dispatch
- `AttuneAuthorHandlers` - Async handlers that implement the six core attune-author tools: `author_init`, `author_status`, `author_generate`, `author_maintain`, `author_docs`, and `author_lookup`

Supporting functions provide server lifecycle management and input validation:

- `create_server()` - Factory function for creating server instances
- `main()` - Server entry point that handles the MCP protocol lifecycle
- `get_tools()` - Returns tool schema definitions for all available tools
- `validate_file_path()` - Validates user-provided file paths against the workspace root

The server accepts an optional workspace root directory at initialization. When no workspace is specified, it operates in the current directory. All file operations are validated against this workspace boundary for security.

## Source files

- `src/attune_author/mcp/server.py` - Server class and entry point
- `src/attune_author/mcp/handlers.py` - Tool implementation handlers
- `src/attune_author/mcp/tool_schemas.py` - MCP tool schema definitions
- `src/attune_author/mcp/path_validation.py` - File path validation utilities

**Tags:** `mcp`, `integration`, `claude-code`
