# attune-author

Documentation authoring and maintenance for the attune
ecosystem.

```
attune-help (reader) --> attune-author (authoring) --> attune-ai (full workflows)
```

## Installation

```bash
pip install attune-author           # Core (templates, staleness)
pip install 'attune-author[ai]'     # + AI-powered doc generation
pip install 'attune-author[rich]'   # + Rich CLI formatting
```

## Quick Start

```bash
# Initialize help system in your project
attune-author init

# Check which templates are stale
attune-author status

# Generate templates for a feature
attune-author generate security-audit

# Regenerate all stale templates
attune-author regenerate
```

## Python API

```python
from attune_author import load_manifest, check_staleness

# Load your project's feature manifest
manifest = load_manifest(".help/features.yaml")

# Check which features have stale documentation
report = check_staleness(".help/")
for feature in report.stale:
    print(f"  {feature.name}: {feature.reason}")
```

## Features

- **Manifest parsing** -- Load and validate
  `.help/features.yaml`
- **Staleness detection** -- Track source hash drift,
  detect outdated templates
- **Template generation** -- Jinja2-based concept, task,
  and reference templates
- **LLM polish** -- Optional AI pass to improve generated
  content (requires `[ai]`)
- **Bulk maintenance** -- Regenerate stale templates in
  one command
- **API reference** -- Generate docs from Python source
  (requires `[ai]`)
- **CLI** -- `attune-author` command for all operations
- **MCP server** -- Expose every CLI capability to Claude
  Code as callable tools (`author_status`,
  `author_generate`, `author_maintain`, `author_lookup`,
  `author_docs`, `author_init`)

## MCP Integration

To make `attune-author` available to Claude Code as tools,
add this to `.mcp.json` in your project:

```json
{
  "mcpServers": {
    "attune-author": {
      "command": "uv",
      "args": ["run", "python", "-m", "attune_author.mcp.server"]
    }
  }
}
```

Then ask Claude things like "are my help templates up to
date?" or "regenerate the stale ones" — it will call the
corresponding MCP tools directly.

## Automation

Ship an always-fresh help tree by wiring up the post-commit
hook:

```bash
git config core.hooksPath .githooks   # one-time setup
# or: make setup   (also installs dev deps)
```

After each commit the hook diffs what changed, matches the
files against your manifest, and regenerates only the
affected templates.

## Development

```bash
make setup        # Install dev deps + configure git hooks
make test         # Run the full test suite
make lint         # ruff check
make status       # Check template staleness
make regenerate   # Regenerate stale templates
```

## Ecosystem

| Package | Role | Deps |
|---------|------|------|
| `attune-help` | Read and render help content | 1 (frontmatter) |
| `attune-author` | Author, generate, maintain docs | 4 (jinja2, frontmatter, pyyaml, attune-help) |
| `attune-ai` | Full developer workflow OS | Many |

## License

Apache 2.0
