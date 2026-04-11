---
type: comparison
feature: mcp-server
depth: comparison
generated_at: 2026-04-11T04:59:55.723771+00:00
source_hash: d99e670e0306a6da8972a9bf7c1b94a808c3f1fb3c17fad5dee28bdc1183bac4
status: generated
---

# MCP Server vs Direct API Usage

## What is the MCP Server?

The MCP server exposes attune-author's six core capabilities as Model Context Protocol tools that Claude Code can call directly. Instead of you manually running commands, Claude can invoke `author_init`, `author_generate`, `author_maintain`, and other operations through the standardized MCP interface.

## Integration Approaches

| Approach | Setup Complexity | Claude Integration | Error Handling | Best For |
|----------|------------------|-------------------|----------------|----------|
| **MCP Server** | Medium (protocol setup) | Native tool calling | Structured responses | Interactive AI workflows |
| **Direct CLI** | Low (just run commands) | Copy/paste results | Manual interpretation | One-off tasks |
| **Python API** | Low (import modules) | No integration | Custom handling | Scripted automation |

## MCP Server Advantages

- **Native AI integration**: Claude Code calls tools directly without copy/paste
- **Structured responses**: All results return as JSON with consistent error reporting
- **Workspace isolation**: Built-in path validation prevents directory traversal
- **Async-ready**: Handlers support concurrent operations for better performance

## Direct Usage Disadvantages

- **Manual coordination**: You copy outputs between Claude and your terminal
- **Context loss**: Claude can't see command results unless you paste them back
- **No validation**: CLI tools trust your file paths without MCP's safety checks
- **Fragmented workflow**: Switching between chat and terminal breaks AI assistance flow

## Use the MCP Server when you want to:

- **Collaborate with Claude** on iterative documentation improvements
- **Automate multi-step workflows** where Claude decides the next action based on results
- **Maintain consistency** across documentation sessions with structured tool responses
- **Leverage AI planning** for complex documentation maintenance tasks

## Use direct CLI/API when you need to:

- **Run one-off commands** without setting up MCP protocol integration
- **Script custom workflows** that don't require AI decision-making
- **Integrate with existing automation** that can't use MCP tools
- **Debug tool behavior** by examining raw outputs without MCP wrapper overhead

## Source files

- `src/attune_author/mcp/server.py`
- `src/attune_author/mcp/handlers.py`
- `src/attune_author/mcp/tool_schemas.py`
- `src/attune_author/mcp/path_validation.py`

**Tags:** `mcp`, `integration`, `claude-code`
