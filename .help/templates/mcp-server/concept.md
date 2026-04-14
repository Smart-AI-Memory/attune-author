---
type: concept
feature: mcp-server
depth: concept
generated_at: 2026-04-14T16:15:21.471572+00:00
source_hash: 05e470fa9511d5f688563c951fcd05ded9d16bcb0a768159c902d303a6418936
status: generated
---

# MCP Server

## Architecture

The MCP server exposes attune-author's documentation generation capabilities to Claude Code through the Model Context Protocol, transforming attune-author into a set of callable tools that external AI systems can invoke directly.

The server operates through two complementary layers:

- **`AttuneAuthorMCPServer`** — Protocol adapter that handles MCP communication, maintains a tool registry, and routes incoming requests to the appropriate handlers
- **`AttuneAuthorHandlers`** — Business logic layer containing async implementations for each of the six available tools

When Claude Code needs to bootstrap a help system, check template freshness, or generate documentation, it sends structured requests through the MCP protocol. The server validates inputs using `validate_file_path()` to prevent directory traversal attacks, then delegates to handlers that invoke attune-author's core functionality.

## Available tools

The server exposes six distinct capabilities:

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `author_init` | Bootstrap `.help/` directory and scan for features | `project_root` |
| `author_status` | Report which templates are stale by comparing source hashes | `help_dir`, `project_root` |
| `author_generate` | Generate concept, task, and reference templates for one feature | `feature`, `overwrite` |
| `author_maintain` | Batch regenerate all stale templates in one pass | `features`, `dry_run` |
| `author_docs` | Generate documentation using the 3-stage AI pipeline | `target`, `doc_type`, `audience` |
| `author_lookup` | Retrieve help content by topic name or tag | `query`, `depth` |

Each tool accepts structured JSON arguments and returns results in a consistent format, enabling Claude Code to chain operations like checking status, then generating specific templates, then looking up the results.

## Security boundaries

The server implements path validation to constrain file access within safe boundaries. The `validate_file_path()` function prevents access to system directories like `/etc`, `/proc`, and `/usr/bin`, while ensuring all operations stay within the designated project workspace.
