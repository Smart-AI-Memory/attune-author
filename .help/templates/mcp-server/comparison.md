---
type: comparison
feature: mcp-server
depth: comparison
generated_at: 2026-04-14T16:17:35.806420+00:00
source_hash: 05e470fa9511d5f688563c951fcd05ded9d16bcb0a768159c902d303a6418936
status: generated
---

# MCP server vs direct CLI usage

## Context

The MCP server exposes attune-author's capabilities as Model Context Protocol tools that Claude Code can call directly. This provides a structured API alternative to running command-line operations manually.

## Feature comparison

| Aspect | MCP server | Direct CLI |
|--------|------------|------------|
| **Integration** | Native Claude Code tool calls | Manual command execution |
| **Validation** | Built-in path safety checks | User responsibility |
| **Error handling** | Structured JSON responses | Raw stderr output |
| **Discoverability** | Schema-driven tool descriptions | `--help` flags |
| **Automation** | Programmatic access via Claude | Script-based workflows |
| **Setup overhead** | Server process + MCP registration | Install and run |

## Key tradeoffs

**MCP server advantages:**
- **Claude integration**: Tools appear natively in Claude Code's interface with full schema documentation
- **Safety**: Automatic path validation prevents access to system directories like `/etc` and `/proc`
- **Structured output**: All responses are JSON with consistent error handling
- **Real-time**: No process startup overhead for each operation

**Direct CLI advantages:**
- **Simplicity**: No server setup or MCP configuration required
- **Flexibility**: Full shell scripting and piping capabilities
- **Debugging**: Direct access to verbose logging and intermediate files
- **Standalone**: Works without Claude Code or MCP infrastructure

## Available tools

The MCP server exposes these 6 attune-author operations:

- `author_init` - Bootstrap .help/ directory and scan for features
- `author_status` - Check which templates are stale
- `author_generate` - Create templates for a single feature
- `author_maintain` - Regenerate all stale templates in batch
- `author_docs` - Generate documentation from source files
- `author_lookup` - Query help content by topic or tag

Each tool includes validation and structured error responses that the CLI versions don't provide.

## Use MCP server when...

- You work primarily in Claude Code and want seamless access to attune-author
- You need path safety guarantees (the server blocks dangerous filesystem access)
- You want consistent JSON responses for programmatic processing
- You're building automated workflows that Claude Code will trigger

## Use direct CLI when...

- You're working outside Claude Code or in shell scripts
- You need maximum flexibility for complex piping or batch operations
- You're debugging issues and need verbose logging output
- You want to avoid the overhead of running a server process

## Recommendation

**Start with the MCP server** if you use Claude Code regularly. The safety guarantees and native integration make it the better choice for interactive development. Fall back to direct CLI for scripting, debugging, or when working in environments without MCP support.

## Source files

- `src/attune_author/mcp/server.py`
- `src/attune_author/mcp/handlers.py`
- `src/attune_author/mcp/tool_schemas.py`
- `src/attune_author/mcp/path_validation.py`

**Tags:** `mcp`, `integration`, `claude-code`
