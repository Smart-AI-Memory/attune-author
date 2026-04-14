---
type: note
feature: mcp-server
depth: note
generated_at: 2026-04-14T14:12:23.590348+00:00
source_hash: 05e470fa9511d5f688563c951fcd05ded9d16bcb0a768159c902d303a6418936
status: generated
---

# Note: mcp server

## Context

The MCP server enables Claude Code to access attune-author's documentation generation capabilities through the Model Context Protocol. When you configure Claude Code with this server, the six attune-author tools become available as callable functions within your coding sessions.

## Architecture

The MCP server centers around two main classes that handle different aspects of the protocol:

**AttuneAuthorMCPServer** serves as the protocol endpoint. It registers the six attune-author tools (`author_init`, `author_status`, `author_generate`, `author_maintain`, `author_docs`, `author_lookup`) and routes tool calls to the appropriate handlers. The server maintains a tool schema registry that defines the input parameters and descriptions for each tool.

**AttuneAuthorHandlers** implements the actual tool logic. Each of the six methods corresponds to one attune-author command, accepting structured arguments and returning results that Claude Code can interpret. The handlers operate asynchronously to avoid blocking the MCP protocol during long-running operations like template generation.

## Tool capabilities

The server exposes these tools to Claude Code:

- `author_init` — Bootstrap a `.help/` directory and scan for features
- `author_status` — Report which templates are stale compared to source code
- `author_generate` — Generate templates for a single feature
- `author_maintain` — Regenerate all stale templates in batch
- `author_docs` — Generate standalone documentation using the 3-stage pipeline
- `author_lookup` — Search and retrieve help content by topic

Path validation ensures that user-provided file paths stay within the project boundaries and don't access system directories.

## Entry point

You start the server with `main()`, which creates an `AttuneAuthorMCPServer` instance and begins listening for MCP protocol messages. The `create_server()` function provides a programmatic way to instantiate the server for testing or integration scenarios.

## Source files

- `src/attune_author/mcp/server.py`
- `src/attune_author/mcp/handlers.py`
- `src/attune_author/mcp/tool_schemas.py`
- `src/attune_author/mcp/path_validation.py`

**Tags:** `mcp`, `integration`, `claude-code`
