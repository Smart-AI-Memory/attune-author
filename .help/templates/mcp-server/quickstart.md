---
type: quickstart
feature: mcp-server
depth: quickstart
generated_at: 2026-04-14T16:17:12.354310+00:00
source_hash: 05e470fa9511d5f688563c951fcd05ded9d16bcb0a768159c902d303a6418936
status: generated
---

# Run the attune-author MCP server

Start an MCP server that exposes attune-author's help generation tools to Claude Code.

```bash
python -m attune_author.mcp.server
```

The server starts and listens for MCP requests, printing connection details to stdout.

## Test the server

1. **Connect Claude Code to your server** using the connection details from step 1.

2. **Initialize help for a project** by calling the `author_init` tool:
   ```json
   {
     "tool": "author_init",
     "arguments": {
       "project_root": "/path/to/your/project"
     }
   }
   ```

3. **Verify the connection works** by checking that Claude Code can see all six attune-author tools: `author_init`, `author_status`, `author_generate`, `author_maintain`, `author_docs`, and `author_lookup`.

## Expected output

When the server starts successfully, you'll see:
```
MCP server listening on stdio
Available tools: author_init, author_status, author_generate, author_maintain, author_docs, author_lookup
```

Claude Code should now list attune-author as an available MCP server with 6 callable tools for help system management.

## Next steps

Call the `author_status` tool to see which features in your project need documentation templates.
