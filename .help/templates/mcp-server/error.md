---
type: error
feature: mcp-server
depth: error
generated_at: 2026-04-11T04:58:40.335182+00:00
source_hash: d99e670e0306a6da8972a9bf7c1b94a808c3f1fb3c17fad5dee28bdc1183bac4
status: generated
---

# MCP Server errors

The attune-author MCP server exposes six tools to Claude through the Model Context Protocol. Errors typically occur during server initialization, tool execution, or path validation.

## Common error signatures

- **Tool execution failures**: `RuntimeError` when underlying attune-author operations fail during `call_tool()`
- **Path validation errors**: `ValueError` from `validate_file_path()` when file paths are outside allowed directories
- **Server initialization failures**: `FileNotFoundError` or `PermissionError` when workspace_root is invalid
- **Tool schema errors**: `KeyError` or `TypeError` when tool definitions are malformed
- **MCP protocol violations**: Connection errors when the server doesn't conform to MCP specifications

## Where errors originate

MCP server errors stem from these key components:

- **`AttuneAuthorMCPServer.call_tool()`** — Routes tool calls to handlers and catches execution failures
- **`AttuneAuthorHandlers` methods** — Execute the six attune-author tools (init, status, generate, maintain, docs, lookup)
- **`validate_file_path()`** — Prevents directory traversal attacks by validating user-provided paths
- **`main()`** — Server startup and MCP protocol initialization
- **`get_tools()`** — Tool schema definition and registration

## How to diagnose

1. **Check the tool name and arguments**. Tool execution errors often indicate which of the six attune-author tools failed and what arguments were passed. Invalid tool names trigger immediate failures in `call_tool()`.

2. **Examine path validation failures**. If `validate_file_path()` raises a `ValueError`, the user provided a path outside the allowed workspace directory. Check the workspace_root setting and the specific path that was rejected.

3. **Verify workspace state**. Many tool handler failures occur when the workspace isn't properly initialized or lacks required files. Run `author_status` to check workspace health before debugging specific tool failures.

4. **Test tools individually**. Use the MCP development tools or call `AttuneAuthorHandlers` methods directly to isolate whether the issue is in the MCP protocol layer or the underlying attune-author functionality.

## Source files

- `src/attune_author/mcp/server.py`
- `src/attune_author/mcp/handlers.py`
- `src/attune_author/mcp/tool_schemas.py`
- `src/attune_author/mcp/path_validation.py`

**Tags:** `mcp`, `integration`, `claude-code`
