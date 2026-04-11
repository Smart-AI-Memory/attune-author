---
type: concept
feature: mcp-server
depth: concept
generated_at: 2026-04-11T04:58:12.819682+00:00
source_hash: d99e670e0306a6da8972a9bf7c1b94a808c3f1fb3c17fad5dee28bdc1183bac4
status: generated
---

# MCP Server

## How it works

The MCP server exposes attune-author's documentation capabilities as callable tools through the Model Context Protocol, allowing Claude Code to initialize projects, generate documentation, and maintain code quality.

The server architecture consists of two layers:

- **`AttuneAuthorMCPServer`** — The protocol interface that handles MCP communication and tool registration
- **`AttuneAuthorHandlers`** — The implementation layer that executes the six core operations: `author_init`, `author_status`, `author_generate`, `author_maintain`, `author_docs`, and `author_lookup`

When Claude Code calls a tool, the server validates file paths against the workspace root, then delegates to the appropriate handler method. Each handler returns structured responses that Claude can interpret and act upon.

## Available tools

The server exposes six tools that mirror attune-author's command-line interface:

| Tool | Handler Method | Purpose |
|------|---------------|---------|
| `author_init` | `author_init()` | Initialize new documentation projects |
| `author_status` | `author_status()` | Check project health and coverage |
| `author_generate` | `author_generate()` | Create documentation from source code |
| `author_maintain` | `author_maintain()` | Update existing documentation |
| `author_docs` | `author_docs()` | Generate comprehensive documentation sets |
| `author_lookup` | `author_lookup()` | Query project structure and metadata |

## Security model

Path validation ensures Claude can only access files within the configured workspace root. The `validate_file_path()` function normalizes paths and prevents directory traversal attacks, making it safe to expose file operations through the MCP interface.
