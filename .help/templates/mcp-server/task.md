---
type: task
feature: mcp-server
depth: task
generated_at: 2026-04-14T14:10:34.010137+00:00
source_hash: 05e470fa9511d5f688563c951fcd05ded9d16bcb0a768159c902d303a6418936
status: generated
---

# Work with mcp server

Use the MCP server when you need to expose attune-author's documentation capabilities as tools that Claude can call through the Model Context Protocol.

## Prerequisites

- Access to the project source code
- Familiarity with the MCP server files in `src/attune_author/mcp/`

## Start the server

1. **Create a server instance**:
   ```python
   from attune_author.mcp.server import create_server
   server = create_server()
   ```

2. **Run the entry point**:
   ```bash
   python -m attune_author.mcp.server
   ```

## Add new tools

1. **Define the tool schema** in `src/attune_author/mcp/tool_schemas.py`:
   - Add your tool definition to the `get_tools()` function return dictionary
   - Include a clear description and input schema following the existing pattern

2. **Implement the handler** in `src/attune_author/mcp/handlers.py`:
   - Add a method to `AttuneAuthorHandlers` class
   - Follow the async signature: `async def your_tool(self, args: dict[str, Any]) -> dict[str, Any]`

3. **Register the tool** in `src/attune_author/mcp/server.py`:
   - Update `AttuneAuthorMCPServer.call_tool()` to route your tool name to the handler

## Modify existing tools

1. **Identify the tool** you want to change from the six available tools:
   - `author_init` - Bootstrap .help/ directory
   - `author_status` - Check template freshness
   - `author_generate` - Create templates for one feature
   - `author_maintain` - Regenerate all stale templates
   - `author_docs` - Generate documentation from source
   - `author_lookup` - Find help by topic

2. **Update the handler** in `AttuneAuthorHandlers`:
   - Modify the corresponding method (e.g., `author_init()` for the init tool)
   - Preserve the async signature and return format

3. **Update the schema** if you change parameters:
   - Edit the tool definition in `get_tools()`
   - Ensure required fields are marked correctly

## Test your changes

1. **Run targeted tests**:
   ```bash
   pytest -k "mcp" tests/
   ```

2. **Verify tool registration**:
   ```python
   from attune_author.mcp.tool_schemas import get_tools
   tools = get_tools()
   print(list(tools.keys()))  # Should include your tool
   ```

## Success criteria

- The server starts without errors
- Your new or modified tools appear in the tool registry
- Claude can successfully call your tools through the MCP interface
- All existing tests continue to pass
