---
type: tip
feature: mcp-server
depth: tip
generated_at: 2026-04-14T14:12:18.765549+00:00
source_hash: 05e470fa9511d5f688563c951fcd05ded9d16bcb0a768159c902d303a6418936
status: generated
---

# Use `create_server()` for MCP server instances

Call `create_server()` instead of instantiating `AttuneAuthorMCPServer` directly when you need a fresh server instance. The factory function handles workspace root detection and ensures proper initialization, while the constructor requires you to manage these details yourself.

This approach reduces setup errors and keeps your code compatible with future server configuration changes.
