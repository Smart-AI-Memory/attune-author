---
type: comparison
feature: mcp-server
depth: comparison
generated_at: 2026-04-14T14:12:35.874434+00:00
source_hash: 05e470fa9511d5f688563c951fcd05ded9d16bcb0a768159c902d303a6418936
status: generated
---

# MCP Server vs direct CLI usage

## Context

You can access attune-author's features in two ways: through the Model Context Protocol (MCP) server that exposes 6 tools to Claude Code, or by calling the CLI commands directly. Both approaches give you the same core functionality—generating and maintaining documentation templates—but differ significantly in workflow and integration.

## Feature comparison

| Aspect | MCP Server | Direct CLI |
|--------|------------|------------|
| **Access method** | Through Claude Code's MCP interface | Command-line tool |
| **Tool discovery** | 6 pre-defined tools with schemas | Manual command lookup |
| **Input validation** | Automatic via JSON schemas | Manual parameter checking |
| **Error handling** | Structured JSON responses | Text-based error messages |
| **Workspace safety** | Built-in path validation with system directory protection | Relies on shell permissions |
| **Interactive workflow** | Conversational with Claude | One-shot commands |
| **Batch operations** | Requires multiple tool calls | Single command for bulk operations |
| **Setup complexity** | Requires MCP client configuration | Direct installation |

## Use MCP Server when...

Choose the MCP server if you:

- **Work primarily in Claude Code** and want attune-author integrated into your AI workflow
- **Prefer conversational interfaces** where you can ask Claude to "check which templates are stale" rather than remembering CLI syntax
- **Need input validation** — the server prevents path traversal attacks and validates all parameters against JSON schemas
- **Want guided workflows** — Claude can walk you through multi-step processes like "initialize project → generate templates → check status"
- **Share projects with others** who may not be familiar with attune-author's CLI options

The MCP server's strongest advantage is **seamless integration**: Claude can chain operations intelligently, like running `author_status` to find stale templates, then calling `author_generate` for each one.

## Use direct CLI when...

Choose direct CLI access if you:

- **Prefer traditional command-line workflows** and already have attune-author installed
- **Need maximum performance** — CLI commands avoid the JSON serialization overhead of MCP calls
- **Want to script operations** in shell scripts, makefiles, or CI pipelines where MCP isn't available
- **Work offline** or in environments without Claude Code access
- **Need the full range of options** — some advanced CLI flags may not be exposed through the MCP interface

The CLI's main advantage is **simplicity**: no additional setup required, and you get the raw tool output without MCP wrapping.

## Recommendation

**Use the MCP server** as your primary interface if you're already working in Claude Code. The conversational workflow and automatic input validation make it safer and more intuitive than memorizing CLI commands.

**Keep the CLI as backup** for automation scripts and situations where you need direct access outside of Claude's environment. Most users will find the MCP server more convenient for day-to-day documentation maintenance.

## Source files

- `src/attune_author/mcp/server.py`
- `src/attune_author/mcp/handlers.py`
- `src/attune_author/mcp/tool_schemas.py`
- `src/attune_author/mcp/path_validation.py`

**Tags:** `mcp`, `integration`, `claude-code`
