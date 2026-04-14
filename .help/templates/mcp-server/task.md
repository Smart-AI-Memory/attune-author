---
type: task
feature: mcp-server
depth: task
generated_at: 2026-04-14T16:15:33.250705+00:00
source_hash: 05e470fa9511d5f688563c951fcd05ded9d16bcb0a768159c902d303a6418936
status: generated
---

# Work with mcp server

Use the MCP server when you need to expose attune-author's documentation generation capabilities as Model Context Protocol tools for Claude or other AI assistants.

## Prerequisites

- Access to the project source code
- Familiarity with the MCP server implementation in `src/attune_author/mcp/`

## Start the server

1. **Run the MCP server entry point:**
   ```bash
   python -m attune_author.mcp.server
   ```

2. **Verify the server starts successfully:**
   The server should initialize without errors and begin listening for tool calls.

## Add a new tool

1. **Define the tool schema in `tool_schemas.py`:**
   Add your tool definition to the dictionary returned by `get_tools()`, following the existing pattern with description, input_schema, and required fields.

2. **Implement the handler in `handlers.py`:**
   Add a new async method to the `AttuneAuthorHandlers` class that processes your tool's arguments and returns a result dictionary.

3. **Register the tool in `server.py`:**
   Ensure the `AttuneAuthorMCPServer.call_tool()` method can route to your new handler.

4. **Test the tool integration:**
   Run `pytest -k "mcp"` to verify your changes don't break existing functionality.

## Modify existing tools

1. **Locate the tool definition:**
   Find your target tool in the `get_tools()` return value to understand its current schema and parameters.

2. **Update the handler method:**
   Modify the corresponding method in `AttuneAuthorHandlers` (like `author_generate`, `author_status`, etc.) to implement your changes.

3. **Validate file paths if needed:**
   Use `validate_file_path()` for any user-provided file paths to prevent directory traversal attacks.

4. **Test the modified behavior:**
   Verify that your changes work correctly and don't introduce security vulnerabilities.

## Verify success

The MCP server is working correctly when:
- It starts without errors when you run the main entry point
- Tool calls return expected results without exceptions
- File path validation blocks attempts to access system directories
- Tests pass with `pytest -k "mcp"`

## Key files

- `src/attune_author/mcp/server.py` — Core server and tool dispatcher
- `src/attune_author/mcp/handlers.py` — Tool implementation logic
- `src/attune_author/mcp/tool_schemas.py` — Tool definitions and schemas
- `src/attune_author/mcp/path_validation.py` — Security validation for file paths
