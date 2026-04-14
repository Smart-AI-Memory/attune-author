---
type: warning
feature: mcp-server
depth: warning
generated_at: 2026-04-14T14:11:26.060183+00:00
source_hash: 05e470fa9511d5f688563c951fcd05ded9d16bcb0a768159c902d303a6418936
status: generated
---

# MCP Server cautions

## What to watch for

The MCP server exposes attune-author's capabilities to Claude Code as callable tools. While the integration is designed to be safe, several areas require careful attention to prevent security issues and unexpected behavior.

## Risk areas

### Path traversal in file operations

The `validate_file_path()` function checks for directory traversal attacks, but you can still encounter problems if you bypass validation or misconfigure workspace boundaries. The function rejects paths containing null bytes, system directories (like `/etc`, `/proc`), and paths outside allowed directories, but it won't catch application-logic errors where you pass the wrong base directory.

### Workspace root misconfiguration

Both `AttuneAuthorMCPServer` and `AttuneAuthorHandlers` accept a `workspace_root` parameter. If you set this incorrectly, tools will operate on the wrong project directory. The server defaults to `None` (current directory), while handlers require an explicit path. This mismatch can cause tools to fail silently or modify unexpected files.

### Tool argument validation gaps

MCP tools receive unvalidated JSON from Claude Code. While each tool has a schema definition in `get_tools()`, the server only validates structure, not semantic correctness. For example, `author_generate` requires a valid feature name from `features.yaml`, but the MCP layer won't catch typos or missing features until runtime.

### Async handler context loss

The six tools in `AttuneAuthorHandlers` are async methods, but they run in the MCP server's synchronous `call_tool()` context. If you modify these handlers to perform async operations (like concurrent file I/O), you risk deadlocks or resource leaks because the server doesn't provide proper async context management.

## How to avoid problems

1. **Always validate workspace boundaries.** Before calling any tool that accepts file paths, verify that your workspace_root setting points to the correct project directory and that all operations stay within bounds.

2. **Test with invalid tool arguments.** Claude Code can send malformed requests, so test your MCP integration with missing required fields, wrong data types, and edge cases like empty strings or very long inputs.

3. **Monitor async tool performance.** The MCP server runs tools synchronously, so slow operations will block other requests. If a tool takes more than a few seconds, consider adding timeout handling or breaking large operations into smaller chunks.

4. **Verify feature names before generation.** When using `author_generate` or `author_maintain`, confirm that feature names exist in your `features.yaml` file. These tools will fail with cryptic errors if you reference non-existent features.

## Source files

- `src/attune_author/mcp/server.py`
- `src/attune_author/mcp/handlers.py`
- `src/attune_author/mcp/tool_schemas.py`
- `src/attune_author/mcp/path_validation.py`

**Tags:** `mcp`, `integration`, `claude-code`
