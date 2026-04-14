---
type: faq
feature: mcp-server
depth: faq
generated_at: 2026-04-14T14:12:01.191798+00:00
source_hash: 05e470fa9511d5f688563c951fcd05ded9d16bcb0a768159c902d303a6418936
status: generated
---

# Mcp Server FAQ

## What is mcp server?

An MCP (Model Context Protocol) server that exposes attune-author's six authoring tools to Claude Code and other MCP clients.

## When should I use it?

Use the MCP server when you want to access attune-author's capabilities from Claude Code or another MCP client. It's the bridge that lets external tools call `author_init`, `author_generate`, `author_maintain`, and other commands remotely.

## What tools does it expose?

The server provides six MCP tools:

- `author_init` — Bootstrap a .help/ directory and scan for features
- `author_status` — Check which feature templates are stale
- `author_generate` — Generate templates for a single feature
- `author_maintain` — Regenerate all stale templates at once
- `author_docs` — Generate documentation using the 3-stage pipeline
- `author_lookup` — Look up help content by topic or tag

## How do I start the server?

Call `main()` from `src/attune_author/mcp/server.py`, or use `create_server()` if you need to embed it in another application.

## What's the workspace_root parameter for?

The `workspace_root` parameter sets the base directory for all file operations. If you don't provide it, the server uses the current working directory.

## How do I debug it?

Run the tests first: `pytest -k "mcp-server" -v`. If they pass but your code still fails, add a `logger.debug` statement at the suspected failure point and re-run with logging enabled.

## Where are the source files?

- `src/attune_author/mcp/server.py`
- `src/attune_author/mcp/handlers.py`
- `src/attune_author/mcp/tool_schemas.py`
- `src/attune_author/mcp/path_validation.py`

**Tags:** `mcp`, `integration`, `claude-code`
