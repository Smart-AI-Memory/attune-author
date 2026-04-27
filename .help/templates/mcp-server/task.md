---
type: task
feature: mcp-server
depth: task
generated_at: 2026-04-26T19:49:11.751377+00:00
source_hash: ac562ed08ae3ee05fce7d2be7da63d01dec77f2cc64ab8e75c6cd9b9ea9a676e
status: generated
---

# Work with MCP server

Use the MCP server when you need to expose attune-author's capabilities as callable tools through the Model Context Protocol.

## Prerequisites

- Access to the project source code
- Python development environment set up
- Understanding of MCP (Model Context Protocol) concepts

## Configure the server

1. **Review the server entry point**

   Examine `main()` in `src/attune_author/mcp/server.py` to understand how the server initializes and handles requests.

2. **Set up tool definitions**

   Check `get_tools()` in `src/attune_author/mcp/tool_schemas.py` to see the available tools:
   - `author_init` - Bootstrap help directory
   - `author_status` - Report stale templates
   - `author_generate` - Generate feature templates
   - `author_maintain` - Regenerate stale templates
   - `author_docs` - Generate documentation
   - `author_lookup` - Look up help topics

3. **Configure path validation**

   Use `validate_file_path()` in `src/attune_author/mcp/path_validation.py` to ensure user-provided paths are safe and within allowed directories.

## Start the server

1. **Create a server instance**

   Call `create_server()` to get a fresh `AttuneAuthorMCPServer` with the default workspace root.

2. **Initialize with custom workspace**

   If you need a specific workspace root:
   ```python
   server = AttuneAuthorMCPServer(workspace_root="/path/to/project")
   ```

3. **Run the server**

   Execute the main entry point:
   ```bash
   python -m attune_author.mcp.server
   ```

## Handle tool calls

1. **Process incoming requests**

   The server automatically routes tool calls through `call_tool()` method on `AttuneAuthorMCPServer`.

2. **Access tool handlers**

   Each tool maps to a method in `AttuneAuthorHandlers`:
   - Tool calls validate arguments against schemas
   - Handlers execute the requested operations
   - Results return as structured dictionaries

3. **Handle validation errors**

   Path validation raises `ValueError` with specific messages for:
   - Empty or null paths
   - System directory access attempts
   - Paths outside allowed directories

## Test your setup

Run the MCP server tests to verify everything works:
```bash
pytest -k "mcp"
```

You should see the server respond to tool calls and validate file paths correctly.
