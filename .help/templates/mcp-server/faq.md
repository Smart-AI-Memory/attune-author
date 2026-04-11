---
type: faq
feature: mcp-server
depth: faq
generated_at: 2026-04-11T04:59:25.518544+00:00
source_hash: d99e670e0306a6da8972a9bf7c1b94a808c3f1fb3c17fad5dee28bdc1183bac4
status: generated
---

# Mcp Server FAQ

## What is the MCP server?

The MCP server is a Model Context Protocol server that exposes attune-author's capabilities to Claude Code as callable tools. It lets Claude interact with your attune-author workspace through six specific tools.

## When should I use the MCP server?

Use the MCP server when you want Claude Code to perform attune-author operations on your behalf. This includes initializing projects, checking status, generating content, maintaining documentation, and looking up information in your workspace.

## How do I start the MCP server?

Call `main()` to start the server, or use `create_server()` if you need to create a server instance programmatically. The server runs continuously and handles tool requests from Claude Code.

## What tools does the MCP server provide?

The server provides six tools handled by `AttuneAuthorHandlers`:
- `author_init` - Initialize a new workspace
- `author_status` - Check workspace status
- `author_generate` - Generate content
- `author_maintain` - Maintain documentation
- `author_docs` - Work with documentation
- `author_lookup` - Look up information

## How do I get the available tools?

Use `get_tools()` to retrieve all tool definitions with their schemas. This returns the complete specification of what tools are available and how to call them.

## How do I debug MCP server issues?

Run the related tests first with `pytest -k "mcp-server" -v`. If tests pass but your code fails, add `logger.debug` statements at suspected failure points and re-run with logging enabled.

## Where are the source files?

- `src/attune_author/mcp/server.py` - Main server class and entry point
- `src/attune_author/mcp/handlers.py` - Tool handlers implementation
- `src/attune_author/mcp/tool_schemas.py` - Tool definitions and schemas
- `src/attune_author/mcp/path_validation.py` - Path validation utilities

**Tags:** `mcp`, `integration`, `claude-code`
