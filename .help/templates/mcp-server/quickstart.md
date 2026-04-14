---
type: quickstart
feature: mcp-server
depth: quickstart
generated_at: 2026-04-14T14:12:10.445206+00:00
source_hash: 05e470fa9511d5f688563c951fcd05ded9d16bcb0a768159c902d303a6418936
status: generated
---

# Quickstart: MCP server

Create an MCP server that exposes attune-author tools to Claude Code:

```python
from attune_author.mcp.server import create_server

server = create_server()
print(f"Created server with {len(server.tools)} tools")
```

## Run the server

1. **Start the MCP server** by running the main entry point:

   ```bash
   python -m attune_author.mcp.server
   ```

2. **Verify tools are available** by checking the server object:

   ```python
   from attune_author.mcp.server import create_server

   server = create_server()
   for name, schema in server.tools.items():
       print(f"Tool: {name} - {schema['description']}")
   ```

   Expected output shows six tools:
   ```
   Tool: author_init - Bootstrap a .help/ directory in the project...
   Tool: author_status - Report which feature templates are stale...
   Tool: author_generate - Generate concept, task, and reference templates...
   Tool: author_maintain - Detect and regenerate all stale feature templates...
   Tool: author_docs - Generate documentation from a source file...
   Tool: author_lookup - Look up help for a topic by name or tag...
   ```

3. **Call a tool** to test the integration:

   ```python
   result = server.call_tool("author_status", {"project_root": "."})
   print(result)
   ```

## Next steps

Configure your Claude Code client to connect to this MCP server endpoint for automated help system management.
