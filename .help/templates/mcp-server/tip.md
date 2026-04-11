---
type: tip
feature: mcp-server
depth: tip
generated_at: 2026-04-11T04:59:42.800998+00:00
source_hash: d99e670e0306a6da8972a9bf7c1b94a808c3f1fb3c17fad5dee28bdc1183bac4
status: generated
---

# Tip: working effectively with mcp server

## Use create_server() for fresh instances

Call `create_server()` instead of instantiating `AttuneAuthorMCPServer` directly when you need a new server instance. This factory function handles workspace detection and server configuration automatically, saving you from managing constructor arguments.

## Validate file paths early with validate_file_path()

Always run user-provided file paths through `validate_file_path()` before processing them in your MCP tool handlers. This function prevents directory traversal attacks and ensures paths stay within allowed boundaries—security issues that are easy to miss but expensive to fix later.

## Source files

- `src/attune_author/mcp/server.py`
- `src/attune_author/mcp/handlers.py`
- `src/attune_author/mcp/tool_schemas.py`
- `src/attune_author/mcp/path_validation.py`

**Tags:** `mcp`, `integration`, `claude-code`
