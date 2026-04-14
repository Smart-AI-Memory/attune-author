---
type: troubleshooting
feature: mcp-server
depth: troubleshooting
generated_at: 2026-04-14T14:11:43.915265+00:00
source_hash: 05e470fa9511d5f688563c951fcd05ded9d16bcb0a768159c902d303a6418936
status: generated
---

# Troubleshoot mcp server

## Before you start

The MCP server exposes attune-author's six tools (init, status, generate, maintain, docs, lookup) to Claude Code through the Model Context Protocol. Issues typically involve tool registration, workspace paths, or API key configuration.

## Symptom table

| If you observe | Check |
|----------------|-------|
| Server won't start | Run `python -m attune_author.mcp.server` and check for import errors or missing dependencies |
| Tool not found errors | Verify the tool name exists in `get_tools()` output: `author_init`, `author_status`, `author_generate`, `author_maintain`, `author_docs`, `author_lookup` |
| Path validation failures | Check if the path contains null bytes, points outside the workspace, or hits system directories in `_DANGEROUS_PREFIXES` |
| "ANTHROPIC_API_KEY required" errors | Confirm the environment variable is set when using `author_docs` or LLM polish features |
| Tool returns empty/null results | Check workspace_root initialization and whether `.help/` directory structure exists |

## Step-by-step diagnosis

1. **Test the server directly.**
   Create a minimal test to isolate the MCP server from Claude Code:
   ```python
   from attune_author.mcp.server import create_server
   server = create_server()
   result = server.call_tool('author_status', {'help_dir': '.help'})
   ```

2. **Check tool registration.**
   Verify all six tools are properly registered:
   ```python
   from attune_author.mcp.tool_schemas import get_tools
   tools = get_tools()
   print(list(tools.keys()))  # Should show all 6 author_* tools
   ```

3. **Validate workspace setup.**
   Many tools require a properly initialized workspace:
   - Check if `.help/` directory exists
   - Verify `features.yaml` is present and readable
   - Confirm project_root points to the correct directory

4. **Test path validation separately.**
   Path issues often cause silent failures:
   ```python
   from attune_author.mcp.path_validation import validate_file_path
   validate_file_path('/etc/passwd')  # Should raise ValueError
   validate_file_path('src/main.py')  # Should succeed
   ```

## Common fixes

- **Initialize the workspace first.** Run the `author_init` tool to create the `.help/` directory structure before using other tools.

- **Set ANTHROPIC_API_KEY.** The `author_docs` tool and LLM polish features require this environment variable:
  ```bash
  export ANTHROPIC_API_KEY=your_key_here
  ```

- **Fix workspace_root configuration.** If tools can't find your project files, explicitly set the workspace root:
  ```python
  from attune_author.mcp.server import AttuneAuthorMCPServer
  server = AttuneAuthorMCPServer(workspace_root='/path/to/your/project')
  ```

- **Check file permissions.** The server needs read access to source files and write access to the `.help/` directory.

- **Update the MCP client.** If Claude Code shows connection errors, restart it or check for MCP protocol version mismatches.

## Source files

- `src/attune_author/mcp/server.py`
- `src/attune_author/mcp/handlers.py`
- `src/attune_author/mcp/tool_schemas.py`
- `src/attune_author/mcp/path_validation.py`

**Tags:** `mcp`, `integration`, `claude-code`
