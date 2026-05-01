# attune-author

Create and maintain **dynamic, context-sensitive help** for
your codebase — help content that stays in sync with source
and is served on demand at the right depth to whoever asks:
a human reader, an IDE, or an AI coding assistant over MCP.

Not a static docs site and not a wiki. Help content is
authored as a manifest of features, generated from source
(concept → task → reference depths), tracked by content
hash, regenerated when source drifts, and delivered
progressively so readers — human or AI — get exactly the
depth they asked for.

```
attune-help (reader) --> attune-author (authoring) --> attune-ai (full workflows)
```

## Installation

```bash
pip install attune-author           # Core (templates, staleness)
pip install 'attune-author[ai]'     # + AI-powered doc generation
pip install 'attune-author[rag]'    # + RAG-grounded polish (see below)
pip install 'attune-author[rich]'   # + Rich CLI formatting
```

### RAG-grounded polish (optional)

When `attune-author[rag]` is installed, the LLM polish pass
consults existing attune-help templates via
[attune-rag](https://github.com/Smart-AI-Memory/attune-rag)
before rewriting your generated template. It surfaces
related templates as style and naming references so the
polished output stays consistent with the wider
ecosystem's conventions — not to copy content, but to keep
headings, terminology, and structure aligned.

Grounding is **on by default** when the extra is
installed. To disable per-invocation:

```bash
attune-author generate my-feature --no-rag
```

To disable globally (e.g. in CI for deterministic output):

```bash
ATTUNE_AUTHOR_RAG=0 attune-author generate my-feature
```

Without the `[rag]` extra installed, `attune-author`
proceeds as before — no behavior change.

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

## Polish cache

`attune-author` caches LLM polish responses on disk so re-generating an
already-polished template is instant and costs zero tokens. The cache
lives at `~/.attune/polish_cache/` by default.

```bash
# View cache stats (entries, size)
attune-author cache status

# Flush all entries (e.g. after a major prompt change)
attune-author cache clear
```

**Environment variables**

| Variable | Default | Effect |
|----------|---------|--------|
| `ATTUNE_AUTHOR_POLISH_CACHE` | `~/.attune/polish_cache` | Override cache directory |
| `ATTUNE_AUTHOR_POLISH_CACHE_TTL_SECONDS` | `2592000` (30 days) | TTL in seconds; `0` disables expiry |

Cache entries are keyed by a SHA-256 hash of the content (with
volatile frontmatter fields like `generated_at` stripped),
`source_summary`, `template_type`, system prompt, augmented RAG
context, and model name. Changing the model automatically invalidates
all prior entries.

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

- **Progressive-depth templates** -- Every feature gets a
  concept (overview), task (how-to), and reference (API)
  view, plus optional problem-shaped (error, warning,
  troubleshooting, faq) and guidance-shaped (quickstart,
  tip, note, comparison) kinds
- **Project-doc generation** -- Four additional kinds
  (`how-to`, `tutorial`, `cli-reference`, `architecture`)
  render to `docs/` for end-user consumption. These use
  HTML comment footers for staleness tracking instead of
  YAML frontmatter, so the output is clean plain markdown.
  Run `attune-author generate <feature> --all-kinds` to
  produce both `.help/` templates and `docs/` output in
  one pass
- **Context-sensitive delivery** -- Readers fetch only the
  depth they need via `attune-help`; AI assistants pull
  the right slice through the MCP `author_lookup` tool
- **Staleness detection** -- Source-hash drift is tracked
  in template frontmatter; drift triggers regeneration on
  the next `regenerate` or post-commit hook
- **Grounded generation** -- Templates are rendered from
  the actual source AST (signatures, defaults, raises
  with diagnostic messages, dataclass fields, Literal
  enums, `@property` accessors, module-level string
  constants), optionally polished by an LLM against a
  strict source-info anchor that separates prose from
  verbatim facts
- **Bulk maintenance** -- Regenerate every stale feature
  in one command, or let the post-commit hook do it for
  you scoped to files that actually changed
- **CLI** -- `attune-author` for all operations
- **MCP server** -- Six tools (`author_init`,
  `author_status`, `author_generate`, `author_maintain`,
  `author_lookup`, `author_docs`) that make every CLI
  capability callable by Claude Code and any other MCP
  client

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
