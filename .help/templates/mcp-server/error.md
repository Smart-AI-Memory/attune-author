---
type: error
feature: mcp-server
depth: error
generated_at: 2026-04-14T14:11:12.513385+00:00
source_hash: 05e470fa9511d5f688563c951fcd05ded9d16bcb0a768159c902d303a6418936
status: generated
---

# MCP server errors

Failures in the Model Context Protocol server that exposes attune-author's documentation tools to Claude Code.

## Common error signatures

**Path validation errors:**
- `ValueError: path must be a non-empty string`
- `ValueError: path contains null bytes`
- `ValueError: Path is outside the project: /etc is a system directory`
- `ValueError: Invalid path: <path>`
- `ValueError: Path '/some/path' is outside allowed directory '/project'`

**Tool execution errors:**
- `KeyError` when required tool arguments are missing
- `FileNotFoundError` when workspace_root or help directories don't exist
- Authentication errors when ANTHROPIC_API_KEY is required but missing

## Where errors originate

The MCP server has four main failure points:

- **Server initialization** in `AttuneAuthorMCPServer.__init__()` — Invalid workspace_root paths
- **Tool dispatch** in `AttuneAuthorMCPServer.call_tool()` — Unknown tool names or malformed arguments
- **Path validation** in `validate_file_path()` — Security checks that reject dangerous or invalid paths
- **Tool handlers** in `AttuneAuthorHandlers` methods — Feature-specific failures like missing API keys or invalid project structure

## How to diagnose

1. **Check the tool name and arguments.** Most MCP errors stem from incorrect tool calls. Verify that the tool name matches one of the six supported tools (`author_init`, `author_status`, `author_generate`, `author_maintain`, `author_docs`, `author_lookup`) and that required arguments are provided.

2. **Validate the workspace setup.** If you see path-related errors, ensure the workspace_root exists and is accessible. The server defaults to the current working directory if no workspace_root is specified.

3. **Review path restrictions.** Path validation rejects system directories (`/etc`, `/sys`, `/proc`, etc.) and paths outside the allowed workspace. Check that file paths in tool arguments point to locations within your project.

4. **Verify environment prerequisites.** The `author_docs` tool requires ANTHROPIC_API_KEY. The `author_*` tools expect a `.help/` directory structure created by `author_init`.

## Source files

- `src/attune_author/mcp/server.py`
- `src/attune_author/mcp/handlers.py`
- `src/attune_author/mcp/tool_schemas.py`
- `src/attune_author/mcp/path_validation.py`

**Tags:** `mcp`, `integration`, `claude-code`
