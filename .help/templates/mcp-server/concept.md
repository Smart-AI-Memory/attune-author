---
type: concept
feature: mcp-server
depth: concept
generated_at: 2026-04-12T04:52:21.501576+00:00
source_hash: ede5ab36c4a3cf2b73e64330e50a7c9cd90cbe45b9b8d5be3909ee9d4c036883
status: generated
---

# MCP Server

## How it works

The MCP (Model Context Protocol) server exposes attune-author's documentation workflow as callable tools that Claude Code can invoke directly.

When Claude Code connects to this server, it gains access to six attune-author operations:
- `author_init` — Initialize a new documentation project
- `author_status` — Check the current project state
- `author_generate` — Create documentation from source code
- `author_maintain` — Update existing documentation
- `author_docs` — Generate API documentation
- `author_lookup` — Search for specific documentation elements

The server architecture separates concerns between tool registration and execution:

- **`AttuneAuthorMCPServer`** handles the MCP protocol, registering tools and routing calls
- **`AttuneAuthorHandlers`** implements the actual business logic for each tool

All file paths that users provide through the MCP interface pass through `validate_file_path()` to prevent directory traversal attacks and ensure operations stay within the designated workspace.

## Integration points

The MCP server connects attune-author to external AI coding assistants, particularly Claude Code. You can start the server using the `main()` entry point or create instances programmatically with `create_server()`.

Tool definitions are centralized in `get_tools()`, which returns the schema that Claude Code uses to understand what each tool does and what arguments it expects.
