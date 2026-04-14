---
type: concept
feature: mcp-server
depth: concept
generated_at: 2026-04-14T14:10:22.395227+00:00
source_hash: 05e470fa9511d5f688563c951fcd05ded9d16bcb0a768159c902d303a6418936
status: generated
---

# MCP Server

## How it works

The MCP server exposes attune-author's documentation generation capabilities to Claude through the Model Context Protocol, allowing you to bootstrap help systems, generate templates, and maintain documentation directly from your editor.

The server architecture centers on two classes:

- **`AttuneAuthorMCPServer`** — Routes tool calls and manages the schema registry for all six MCP tools
- **`AttuneAuthorHandlers`** — Executes the actual documentation operations like `author_generate` and `author_maintain`

When Claude calls a tool, the server validates the request against predefined schemas, then delegates to the appropriate handler method. For example, calling `author_init` triggers the bootstrap process that scans your project and creates a `.help/` directory with `features.yaml`.

## Available tools

The server exposes six tools that mirror attune-author's command-line interface:

- **`author_init`** — Bootstraps a `.help/` directory by scanning for features and creating `features.yaml`
- **`author_status`** — Reports which templates are stale by comparing source file hashes
- **`author_generate`** — Creates concept, task, and reference templates for a single feature
- **`author_maintain`** — Detects and regenerates all stale templates in one pass
- **`author_docs`** — Generates documentation from source files using the 3-stage LLM pipeline
- **`author_lookup`** — Retrieves help content by feature name, tag, or substring

Each tool accepts structured arguments and returns JSON responses, making them suitable for integration with Claude's tool-calling capabilities.

## Security model

The server includes path validation through `validate_file_path()` to prevent directory traversal attacks. This function blocks access to system directories like `/etc`, `/proc`, and `/usr/bin`, ensuring that MCP tools can only operate on your project files and the designated `.help/` directory.
