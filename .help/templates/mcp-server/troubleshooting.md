---
type: troubleshooting
feature: mcp-server
depth: troubleshooting
generated_at: 2026-04-14T16:16:45.430101+00:00
source_hash: 05e470fa9511d5f688563c951fcd05ded9d16bcb0a768159c902d303a6418936
status: generated
---

# Troubleshoot MCP server

## Before you start

The MCP server exposes attune-author's six tools (init, status, generate, maintain, docs, lookup) to Claude Code through the Model Context Protocol. Issues typically stem from tool execution failures, path validation errors, or workspace configuration problems.

## Symptom table

| If you observe | Check |
|----------------|-------|
| Tool execution fails | Call `AttuneAuthorMCPServer.call_tool()` directly with the same arguments to isolate the handler error |
| Path validation errors | Verify the workspace root is set correctly and paths don't escape allowed directories |
| "Tool not found" errors | Confirm the tool name exists in `get_tools()` output and matches the schema registry |
| API key errors with `author_docs` | Check that `ANTHROPIC_API_KEY` is set in your environment |

## Step-by-step diagnosis

1. **Test the failing tool directly.**
   Before investigating the MCP layer, confirm the underlying tool works:
   ```python
   from attune_author.mcp.handlers import AttuneAuthorHandlers
   handlers = AttuneAuthorHandlers(workspace_root="/path/to/project")
   result = handlers.author_status({"help_dir": ".help"})
   ```

2. **Check the server configuration.**
   Verify the server initializes with the correct workspace:
   ```python
   from attune_author.mcp.server import create_server
   server = create_server()
   print(server.tools)  # Should show all 6 tools
   ```

3. **Validate path inputs.**
   Path validation is strict to prevent directory traversal:
   ```python
   from attune_author.mcp.path_validation import validate_file_path
   validate_file_path("../../../etc/passwd")  # Should raise ValueError
   ```

4. **Enable debug logging.**
   Set logging to DEBUG level before calling `main()` to see detailed execution traces.

## Common fixes

- **Set the workspace root explicitly.** If tools fail with path errors, initialize `AttuneAuthorMCPServer` with an explicit `workspace_root` parameter instead of relying on the default.

- **Install required dependencies.** The `author_docs` tool requires the Anthropic SDK. Install it with `pip install anthropic`.

- **Initialize the help system first.** Most tools expect a `.help/` directory with `features.yaml`. Run `author_init` before other operations:
  ```json
  {"tool": "author_init", "args": {"project_root": "."}}
  ```

- **Check file permissions.** Tools need read access to source files and write access to the `.help/` directory. Verify permissions with `ls -la .help/`.

- **Escape path separators correctly.** When passing paths through JSON, use forward slashes or escape backslashes properly: `"path/to/file"` not `"path\to\file"`.

## Source files

- `src/attune_author/mcp/server.py`
- `src/attune_author/mcp/handlers.py`
- `src/attune_author/mcp/tool_schemas.py`
- `src/attune_author/mcp/path_validation.py`

**Tags:** `mcp`, `integration`, `claude-code`
