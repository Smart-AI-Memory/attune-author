---
type: task
feature: mcp-server
depth: task
generated_at: 2026-04-11T04:58:22.008351+00:00
source_hash: d99e670e0306a6da8972a9bf7c1b94a808c3f1fb3c17fad5dee28bdc1183bac4
status: generated
---

# Work with mcp server

Use the MCP server when you need to expose attune-author's capabilities as callable tools for Claude through the Model Context Protocol.

## Prerequisites

- Access to the project source code
- Familiarity with the MCP server files under `src/attune_author/mcp/`

## Steps

1. **Review the server architecture.**
   Examine the main components to understand how the MCP server operates:
   - `AttuneAuthorMCPServer` class handles tool registration and execution
   - `AttuneAuthorHandlers` provides async handlers for the 6 attune-author tools
   - Tool schemas define the interface for each available tool
   - Path validation ensures secure file access

2. **Identify the component to modify.**
   Each module has a specific role:
   - Server setup and tool registration: `server.py`
   - Tool execution logic: `handlers.py`
   - Tool definitions and schemas: `tool_schemas.py`
   - File path security: `path_validation.py`

3. **Implement your changes.**
   Maintain consistency with existing patterns:
   - Use the established error handling approach
   - Follow the async/await patterns in handlers
   - Preserve the tool schema structure for MCP compatibility

4. **Test the server functionality.**
   Run targeted tests to verify your changes work correctly:
   ```bash
   pytest -k "mcp" -v
   ```

## Key files

- `src/attune_author/mcp/server.py` — Main server class and entry point
- `src/attune_author/mcp/handlers.py` — Tool execution handlers
- `src/attune_author/mcp/tool_schemas.py` — Tool definitions and schemas
- `src/attune_author/mcp/path_validation.py` — File path security validation

## Verify success

The MCP server works correctly when:
- The server starts without errors using `main()`
- All 6 tools (init, status, generate, maintain, docs, lookup) are registered
- Tool calls return valid responses with proper error handling
- File paths are validated before processing
