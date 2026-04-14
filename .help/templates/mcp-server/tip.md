---
type: tip
feature: mcp-server
depth: tip
generated_at: 2026-04-14T16:17:20.620286+00:00
source_hash: 05e470fa9511d5f688563c951fcd05ded9d16bcb0a768159c902d303a6418936
status: generated
---

# Use create_server() instead of instantiating AttuneAuthorMCPServer directly

Call `create_server()` to get a configured MCP server instance rather than using the class constructor. The factory function handles workspace root detection and ensures consistent initialization across different environments.

## Why this matters

Direct instantiation requires you to manage workspace root detection yourself, while `create_server()` handles this complexity and provides a stable interface that won't break if the initialization logic changes.
