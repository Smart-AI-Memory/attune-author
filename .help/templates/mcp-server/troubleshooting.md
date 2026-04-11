---
type: troubleshooting
feature: mcp-server
depth: troubleshooting
generated_at: 2026-04-11T04:59:07.810610+00:00
source_hash: d99e670e0306a6da8972a9bf7c1b94a808c3f1fb3c17fad5dee28bdc1183bac4
status: generated
---

# Troubleshoot mcp server

## Before you start

The MCP server exposes attune-author's capabilities to Claude Code as callable tools through the Model Context Protocol. When troubleshooting, remember that failures can occur at three layers: MCP protocol handling, tool invocation, or the underlying attune-author operations.

## Symptom table

| If you observe | Check |
|----------------|-------|
| Server fails to start | `AttuneAuthorMCPServer.__init__()` workspace_root validation and `main()` entry point |
| Tool not found errors | Output of `get_tools()` and the `tools` property registration |
| Tool execution fails | `AttuneAuthorHandlers` method corresponding to the failing tool name |
| Path-related security errors | `validate_file_path()` rejection of the input path |
| Silent tool failures | Return values from `call_tool()` and individual handler methods |

## Step-by-step diagnosis

1. **Test the server in isolation.**
   Create a minimal MCP server instance to confirm basic functionality:
   ```python
   from attune_author.mcp.server import create_server
   server = create_server()
   tools = server.tools()
   print(f"Registered tools: {list(tools.keys())}")
   ```

2. **Check tool registration.**
   Verify all six expected tools are available:
   ```python
   expected_tools = ["author_init", "author_status", "author_generate",
                     "author_maintain", "author_docs", "author_lookup"]
   registered = list(server.tools().keys())
   missing = set(expected_tools) - set(registered)
   ```

3. **Inspect workspace configuration.**
   The server requires a valid workspace root. Check if `workspace_root` is properly set:
   - In `AttuneAuthorMCPServer.__init__()`, verify the path exists
   - In `AttuneAuthorHandlers.__init__()`, confirm workspace initialization succeeded

4. **Test individual tool handlers.**
   Call failing tools directly through the handler layer:
   ```python
   from attune_author.mcp.handlers import AttuneAuthorHandlers
   handlers = AttuneAuthorHandlers("/path/to/workspace")
   result = await handlers.author_status({})  # or whichever tool fails
   ```

## Common fixes

- **Workspace path issues.** Ensure the workspace_root parameter points to a valid directory with appropriate permissions. The server may fail silently if it cannot access the workspace.

- **Missing tool arguments.** Each tool handler expects specific argument structures. Check the tool schema definitions in `get_tools()` and ensure your calls match the expected parameter names and types.

- **Path validation failures.** If you see security-related path errors, verify that `validate_file_path()` accepts your target paths. File operations are restricted to the allowed directory scope.

- **Handler initialization errors.** The `AttuneAuthorHandlers` class requires a valid workspace during initialization. If tools fail consistently, check that the handlers were properly instantiated with a working workspace_root.

- **MCP protocol version mismatch.** Ensure your MCP client (like Claude Code) uses a compatible protocol version with the server implementation.

## Source files

- `src/attune_author/mcp/server.py`
- `src/attune_author/mcp/handlers.py`
- `src/attune_author/mcp/tool_schemas.py`
- `src/attune_author/mcp/path_validation.py`

**Tags:** `mcp`, `integration`, `claude-code`
