---
type: note
feature: mcp-server
depth: note
generated_at: 2026-04-14T16:17:25.239329+00:00
source_hash: 05e470fa9511d5f688563c951fcd05ded9d16bcb0a768159c902d303a6418936
status: generated
---

# Note: mcp server

## Context

The MCP server bridges attune-author's documentation generation capabilities with Claude Code through the Model Context Protocol. It exposes six core tools that handle everything from project initialization to template maintenance and content lookup.

## Architecture

The server implementation centers on two main classes:

- **AttuneAuthorMCPServer** — The protocol server that manages tool registration and request routing
- **AttuneAuthorHandlers** — Async handlers that implement the actual tool logic for each of the six operations

The server exposes these tools through MCP:

- `author_init` — Bootstrap a `.help/` directory and scan for project features
- `author_status` — Report which templates are stale based on source file changes
- `author_generate` — Create concept, task, and reference templates for a single feature
- `author_maintain` — Batch regenerate all stale templates across the project
- `author_docs` — Generate documentation using the 3-stage LLM pipeline
- `author_lookup` — Query help content by feature name, tag, or substring

Each tool validates its file path inputs using `validate_file_path()` to prevent directory traversal attacks. The validation logic specifically blocks access to system directories like `/etc`, `/sys`, and `/proc`.

## Entry points

You can start the server through `main()` or create instances programmatically with `create_server()`. The tool schemas are available separately through `get_tools()` for introspection or testing.

## Source files

- `src/attune_author/mcp/server.py`
- `src/attune_author/mcp/handlers.py`
- `src/attune_author/mcp/tool_schemas.py`
- `src/attune_author/mcp/path_validation.py`

**Tags:** `mcp`, `integration`, `claude-code`
