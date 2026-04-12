---
type: task
feature: mcp-server
depth: task
generated_at: 2026-04-12T04:52:30.394885+00:00
source_hash: ede5ab36c4a3cf2b73e64330e50a7c9cd90cbe45b9b8d5be3909ee9d4c036883
status: generated
---

# Work with mcp server

Use the MCP server when you need to expose attune-author's capabilities as callable tools to Claude through the Model Context Protocol.

## Prerequisites

- Access to the project source code
- Familiarity with the files under `src/attune_author/mcp/`

## Configure the server

1. **Set up the workspace root.**
   Initialize the server with your project's workspace directory:
   ```python
   from attune_author.mcp.server import create_server
   server = create_server()
   ```

2. **Start the MCP server.**
   Run the entry point to begin listening for MCP requests:
   ```python
   from attune_author.mcp.server import main
   main()
   ```

## Add new tools

1. **Define the tool schema.**
   Add your tool definition to `get_tools()` in `src/attune_author/mcp/tool_schemas.py`:
   ```python
   "your_tool_name": {
       "description": "What this tool does",
       "inputSchema": {
           "type": "object",
           "properties": {
               "param_name": {"type": "string", "description": "Parameter description"}
           },
           "required": ["param_name"]
       }
   }
   ```

2. **Implement the tool handler.**
   Add the corresponding handler method to `AttuneAuthorHandlers` in `src/attune_author/mcp/handlers.py`:
   ```python
   async def your_tool_name(self, args: dict[str, Any]) -> dict[str, Any]:
       # Your tool implementation
       return {"result": "success"}
   ```

3. **Register the tool.**
   Update `call_tool()` in `AttuneAuthorMCPServer` to route to your new handler.

## Modify existing tools

1. **Locate the tool handler.**
   Find the corresponding method in `AttuneAuthorHandlers` class:
   - `author_init()` - Initialize new attune-author projects
   - `author_status()` - Check project status
   - `author_generate()` - Generate documentation
   - `author_maintain()` - Maintain existing docs
   - `author_docs()` - Work with documentation
   - `author_lookup()` - Look up project information

2. **Update the implementation.**
   Modify the handler method while preserving its async signature and return type.

3. **Validate file paths.**
   Use `validate_file_path()` for any user-provided file paths to prevent directory traversal attacks.

## Test your changes

Run the MCP server tests to verify your modifications:
```bash
pytest -k "mcp"
```

You'll know the task worked when the tests pass and Claude can successfully call your tools through the MCP protocol.

## Key files

- `src/attune_author/mcp/server.py` - Main server class and entry point
- `src/attune_author/mcp/handlers.py` - Tool implementation logic
- `src/attune_author/mcp/tool_schemas.py` - Tool definitions and schemas
- `src/attune_author/mcp/path_validation.py` - Security validation for file paths
