---
type: error
feature: mcp-server
depth: error
generated_at: 2026-04-14T16:16:13.217377+00:00
source_hash: 05e470fa9511d5f688563c951fcd05ded9d16bcb0a768159c902d303a6418936
status: generated
---

# Mcp Server errors

The attune-author MCP server fails when tool calls are malformed, file paths are invalid, or the workspace is misconfigured.

## Common error signatures

**Path validation failures:**
- `ValueError: path must be a non-empty string`
- `ValueError: path contains null bytes`
- `ValueError: Path is outside the project: /etc is a system directory`
- `ValueError: Invalid path: {path}`
- `ValueError: Path '/some/path' is outside allowed directory '/workspace'`

**Tool invocation failures:**
- `KeyError` when required arguments are missing from tool calls
- `TypeError` when `AttuneAuthorMCPServer.call_tool()` receives invalid argument types
- `FileNotFoundError` when workspace_root doesn't exist during server initialization

## Where errors originate

MCP server errors emerge from these key components:

**Tool execution:** `AttuneAuthorMCPServer.call_tool()` validates tool names and dispatches to the appropriate handler. Invalid tool names or malformed arguments cause immediate failures here.

**Path validation:** `validate_file_path()` rejects paths that contain null bytes, point to system directories, or escape allowed workspace boundaries. All user-provided file paths pass through this validation.

**Handler initialization:** `AttuneAuthorHandlers.__init__()` requires a valid workspace_root. If the directory doesn't exist or isn't accessible, the server can't start.

**Tool schema registry:** `get_tools()` returns the static schema definitions. Schema mismatches between client expectations and server capabilities manifest as argument validation errors.

## How to diagnose

1. **Check the tool call structure.** Verify that required arguments like `feature` for `author_generate` are present and correctly typed. Missing or misnamed arguments trigger immediate validation failures.

2. **Validate file paths separately.** Run `validate_file_path()` directly on suspicious paths to isolate path validation issues from other tool logic. The function provides specific error messages for different path violations.

3. **Verify workspace configuration.** Ensure the workspace_root exists and is readable. The MCP server cannot function without a valid workspace directory.

4. **Test tool schemas.** Compare the client's tool call arguments against the schemas returned by `get_tools()`. Schema mismatches often cause cryptic errors during argument processing.

5. **Check for system path access.** Review any file paths in tool arguments for references to system directories like `/etc`, `/sys`, or `/proc`. The path validator explicitly blocks these dangerous prefixes.

## Source files

- `src/attune_author/mcp/server.py`
- `src/attune_author/mcp/handlers.py`
- `src/attune_author/mcp/tool_schemas.py`
- `src/attune_author/mcp/path_validation.py`

**Tags:** `mcp`, `integration`, `claude-code`
