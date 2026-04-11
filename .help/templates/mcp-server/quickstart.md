---
type: quickstart
feature: mcp-server
depth: quickstart
generated_at: 2026-04-11T04:59:34.607664+00:00
source_hash: d99e670e0306a6da8972a9bf7c1b94a808c3f1fb3c17fad5dee28bdc1183bac4
status: generated
---

# Quickstart: MCP server

```python
from attune_author.mcp.server import create_server

# Create a server instance
server = create_server()

# List available tools
tools = server.tools()
print(f"Available tools: {list(tools.keys())}")
```

This Model Context Protocol server exposes attune-author's capabilities to Claude Code as callable tools.

## Run the server

1. **Create a server instance** with your workspace directory:
   ```python
   from attune_author.mcp.server import create_server

   server = create_server()
   # Or specify a workspace: AttuneAuthorMCPServer("/path/to/workspace")
   ```

2. **Check available tools** to confirm the server is working:
   ```python
   tools = server.tools()
   print(list(tools.keys()))
   ```

3. **Call a tool** to verify the integration:
   ```python
   result = server.call_tool("author_status", {})
   print(result)
   ```

## Expected output

The tools list should show six available commands:
```
['author_init', 'author_status', 'author_generate', 'author_maintain', 'author_docs', 'author_lookup']
```

The status call returns information about your workspace configuration and current state.

## Next steps

Configure your MCP client (like Claude Code) to connect to this server using the `main()` function as the entry point.

## Source files

- `src/attune_author/mcp/server.py`
- `src/attune_author/mcp/handlers.py`
- `src/attune_author/mcp/tool_schemas.py`
- `src/attune_author/mcp/path_validation.py`

**Tags:** `mcp`, `integration`, `claude-code`
