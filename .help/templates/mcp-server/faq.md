---
type: faq
feature: mcp-server
depth: faq
generated_at: 2026-04-14T16:17:02.116025+00:00
source_hash: 05e470fa9511d5f688563c951fcd05ded9d16bcb0a768159c902d303a6418936
status: generated
---

# Mcp Server FAQ

## What is the MCP server?

The MCP server exposes attune-author's functionality as callable tools through the Model Context Protocol, allowing Claude Code to interact with your help system.

## When should I use the MCP server?

Use the MCP server when you want Claude Code to help with documentation tasks like bootstrapping help directories, checking template status, generating docs, or looking up help content. It's designed for IDE integration rather than direct command-line use.

## How do I start the MCP server?

Call `main()` or use `create_server()` to get an `AttuneAuthorMCPServer` instance. The server provides six tools: `author_init`, `author_status`, `author_generate`, `author_maintain`, `author_docs`, and `author_lookup`.

## What tools does the server provide?

The server exposes six attune-author operations:

- **author_init** — Bootstrap a `.help/` directory and scan for features
- **author_status** — Check which templates are stale
- **author_generate** — Generate templates for a single feature
- **author_maintain** — Regenerate all stale templates at once
- **author_docs** — Generate documentation from source files
- **author_lookup** — Find help content by topic or tag

## How do I debug MCP server issues?

Run `pytest -k "mcp-server" -v` to check the tests first. If tools fail, check that your workspace root is valid and that required files (like `features.yaml`) exist. Add debug logging to the handlers in `AttuneAuthorHandlers` to trace tool execution.

## Where are the source files?

- `src/attune_author/mcp/server.py`
- `src/attune_author/mcp/handlers.py`
- `src/attune_author/mcp/tool_schemas.py`
- `src/attune_author/mcp/path_validation.py`

**Tags:** `mcp`, `integration`, `claude-code`
