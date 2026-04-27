---
type: concept
feature: mcp-server
depth: concept
generated_at: 2026-04-26T19:48:57.194076+00:00
source_hash: ac562ed08ae3ee05fce7d2be7da63d01dec77f2cc64ab8e75c6cd9b9ea9a676e
status: generated
---

# MCP Server

## What

The MCP server is a Model Context Protocol implementation that exposes attune-author's six core tools to Claude Code as callable functions. When you use attune-author in Claude Code, you're actually calling through this MCP server, which translates your requests into workspace operations like generating templates, checking status, and looking up documentation.

## Why

Claude Code needs a structured way to interact with attune-author's functionality. Rather than running commands directly, the MCP server provides a safe, validated interface that:

- **Validates all file paths** to prevent access outside the project workspace
- **Exposes consistent tool schemas** so Claude Code knows exactly what parameters each tool accepts
- **Handles async operations** for file I/O and template generation
- **Provides structured error handling** with meaningful error messages

## Architecture

The MCP server has two main components:

**`AttuneAuthorMCPServer`** serves as the protocol interface. It maintains a registry of tool schemas and routes incoming tool calls to the appropriate handlers. When Claude Code requests `author_generate`, the server validates the request format and delegates to the handler layer.

**`AttuneAuthorHandlers`** implements the actual business logic for each tool. Each of the six tools (`author_init`, `author_status`, `author_generate`, `author_maintain`, `author_docs`, `author_lookup`) has its own handler method that performs validation, executes the operation, and returns structured results.

## Tool capabilities

The MCP server exposes six tools that cover the complete attune-author workflow:

| Tool | Purpose | Typical use |
|------|---------|-------------|
| `author_init` | Bootstrap `.help/` directory and discover features | First-time setup in a new project |
| `author_status` | Check which templates are stale | Before regenerating after code changes |
| `author_generate` | Create templates for a specific feature | Adding documentation for new code |
| `author_maintain` | Regenerate all stale templates at once | Bulk updates after refactoring |
| `author_docs` | Generate docs from source files using AI | Creating API references or guides |
| `author_lookup` | Search help content by name or tag | Finding existing documentation |

## Security model

All file operations go through `validate_file_path()`, which prevents access to system directories (`/etc`, `/sys`, `/proc`) and ensures paths stay within the project workspace. The server rejects any path that contains null bytes, resolves to a system directory, or escapes the allowed directory boundary.
