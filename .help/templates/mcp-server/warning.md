---
type: warning
feature: mcp-server
depth: warning
generated_at: 2026-04-14T16:16:28.919644+00:00
source_hash: 05e470fa9511d5f688563c951fcd05ded9d16bcb0a768159c902d303a6418936
status: generated
---

# MCP server cautions

## What to watch for

The attune-author MCP server exposes powerful file system operations to Claude Code through six tools. Path injection and workspace boundaries are the primary security risks.

## Risk areas

### Path traversal in user inputs

The `validate_file_path()` function blocks obvious attacks like `../../../etc/passwd`, but malicious or malformed paths can still slip through:

- Symbolic links that point outside the workspace
- Unicode normalization that bypasses dot-dot checks
- Race conditions where a valid path becomes invalid between validation and use

All six MCP tools accept file paths from Claude Code. Use `validate_file_path()` for every user-controlled path parameter, not just the obvious ones like `project_root`.

### Workspace root confusion

`AttuneAuthorMCPServer` accepts an optional `workspace_root` parameter that defaults to `None`. When `None`, each tool handler resolves paths relative to its own current directory, which may not match Claude's expectation.

This mismatch causes tools to operate on the wrong files, especially when the MCP server runs from a different directory than the project being documented.

### API key exposure in error messages

The `author_docs` and `author_generate` tools require `ANTHROPIC_API_KEY` for LLM features. If the key is missing or invalid, some error paths may leak the key value in exception messages that get returned to Claude Code.

Check error handling in these tools to ensure sensitive environment variables are scrubbed from user-visible output.

## How to avoid problems

1. **Always specify workspace_root.** Don't rely on the default `None` behavior. Pass an explicit workspace directory when creating `AttuneAuthorMCPServer` instances.

2. **Validate paths at tool boundaries.** Call `validate_file_path()` on every path parameter before passing it to file system operations, even if the parameter seems "safe."

3. **Test with hostile inputs.** Include test cases with paths like `..`, `/dev/null`, and Unicode variants in your tool handler tests.

4. **Scrub environment variables from errors.** When catching exceptions that might expose API keys, sanitize the message before returning it to the client.

## Source files

- `src/attune_author/mcp/server.py`
- `src/attune_author/mcp/handlers.py`
- `src/attune_author/mcp/tool_schemas.py`
- `src/attune_author/mcp/path_validation.py`

**Tags:** `mcp`, `integration`, `claude-code`
