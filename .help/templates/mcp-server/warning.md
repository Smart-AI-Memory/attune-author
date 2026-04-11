---
type: warning
feature: mcp-server
depth: warning
generated_at: 2026-04-11T04:58:53.758352+00:00
source_hash: d99e670e0306a6da8972a9bf7c1b94a808c3f1fb3c17fad5dee28bdc1183bac4
status: generated
---

# Mcp Server cautions

## What to watch for

The MCP server exposes attune-author's file operations and code generation capabilities to Claude through the Model Context Protocol. This creates security and reliability risks that require careful handling.

## Risk areas

### Path injection vulnerabilities

`validate_file_path()` is your only defense against directory traversal attacks. User-controlled paths from MCP tool arguments must pass through this function before any file operations. Bypassing validation allows clients to access files outside the workspace boundary.

### Workspace root inconsistencies

The `AttuneAuthorMCPServer` constructor accepts an optional `workspace_root`, but `AttuneAuthorHandlers` requires one. If you create the server with `workspace_root=None`, tool calls will fail with unclear errors when the handlers try to validate paths against a missing root directory.

### Async handler context loss

All six tool handlers (`author_init`, `author_status`, etc.) are async methods, but the MCP server's `call_tool()` method is synchronous. This mismatch can cause context loss if you're not careful about how async operations are awaited within the handler implementations.

### Tool argument validation gaps

Each MCP tool expects specific argument schemas, but the `call_tool()` method receives raw dictionaries. Missing or malformed arguments can cause cryptic failures deep in the handler chain rather than clear validation errors at the entry point.

## How to avoid problems

1. **Always validate file paths.** Never pass user-controlled path strings directly to file operations. Route them through `validate_file_path()` first, even if they seem safe.

2. **Set workspace boundaries explicitly.** Initialize `AttuneAuthorMCPServer` with a concrete `workspace_root` path rather than relying on the default `None`. This prevents runtime errors and makes the security boundary clear.

3. **Test with malicious inputs.** Include path traversal attempts (`../../../etc/passwd`) and invalid tool arguments in your test suite. The MCP protocol doesn't prevent clients from sending hostile data.

4. **Monitor tool execution errors.** Failed tool calls return error dictionaries rather than raising exceptions. Check the return structure before assuming success.

## Source files

- `src/attune_author/mcp/server.py`
- `src/attune_author/mcp/handlers.py`
- `src/attune_author/mcp/tool_schemas.py`
- `src/attune_author/mcp/path_validation.py`

**Tags:** `mcp`, `integration`, `claude-code`
