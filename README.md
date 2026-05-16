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

## Fact-check (post-polish)

Every polished template runs through an AST-based fact-check
pass that verifies four classes of LLM-fabricable detail without
calling an LLM:

- Python imports and `attune.foo.bar` dotted paths resolve in
  the active venv
- `attune <cmd> --flag` references appear in the cached
  `--help` output (findings include version-coupling
  context so the operator knows which version was probed)
- Relative `[label](target.md)` link targets exist
- Counts (`N templates`, `N features`, `N kinds`) match the
  project filesystem / manifest

Defaults to **soft-fail** — findings are appended to the
polished file as an `## Unresolved references` table. Control
via `--fact-check` / `--no-fact-check` on `generate` and
`regenerate`:

```bash
attune-author generate ops-dashboard --fact-check strict
attune-author regenerate --no-fact-check
```

Or via `ATTUNE_AUTHOR_FACT_CHECK` (`off | soft | strict`,
default `soft`) — the env var takes precedence over the CLI
flag so shell-level intent overrides one-off invocations.
Persistent project-level config lives in
`[tool.attune-author.fact-check]` in `pyproject.toml`:

```toml
[tool.attune-author.fact-check]
enabled = true
soft_fail = true
check_python_refs = true
check_cli_refs = true
check_md_links = true
check_numeric_refs = true

[tool.attune-author.fact-check.skip]
"docs/architecture/some-feature.md" = ["check_md_links"]
```

This is Phase 1 of the [polish-fact-check
spec](docs/specs/polish-fact-check/). Phase 2 (ground-truth
context injection) shipped alongside it. Phase 3 (faithfulness
judge) and Phase 4 (tutorial static check) remain on the
roadmap.

## Ground-truth context (polish-prompt injection)

Phase 2 of the polish-fact-check spec changes what the model
sees during the polish pass: three sentinel-tagged blocks
carrying authoritative surface details are injected into the
user message before the source summary, and a short anchoring
clause is appended to the system prompt instructing the model
to only reference names that appear verbatim in those blocks.

The three blocks:

- `<cli_help>`: captured `<cli> <subcommand> --help` output.
  Driven by an optional `cli_command:` field on each feature in
  `features.yaml` (e.g., `cli_command: ops` for a feature whose
  primary UX is `attune ops`). Absence skips this block.
- `<public_api>`: AST-extracted `__all__` lists plus signatures
  for every public function and class in the feature's source
  files.
- `<dataclasses>`: AST-extracted field names + type annotations
  for every public `@dataclass` in the feature's source files.

The combined block list is capped at 5 KB by default. When the
budget is exceeded, blocks drop in this order: dataclasses,
public_api, cli_help — the most authoritative anchor stays the
longest.

Configure via `pyproject.toml`:

```toml
[tool.attune-author.context-injection]
enabled = true
inject_cli_help = true
inject_public_api = true
inject_dataclasses = true
budget_bytes = 5120
cli_executable = "attune"
```

The goal is to prevent the six hallucination shapes documented
in attune-ai PR #351's ops-dashboard editorial pass (invented
CLI flags, fabricated private-module imports, wrong route
paths, hallucinated counts) at the prompt layer, rather than
relying solely on the post-generation fact-check to catch them.

## Faithfulness review (Phase 3)

The Phase 3 faithfulness judge wraps
`attune_rag.eval.faithfulness.FaithfulnessJudge` as a
post-polish step: it scores each polished file's claims against
the source files it was generated from. When the score falls
below the configured threshold, a `## Faithfulness review`
block is appended to the polished file listing the unsupported
claims and the judge's reasoning.

The judge is **opt-in** because it makes real Anthropic API
calls. To enable:

```toml
[tool.attune-author.fact-check.faithfulness]
enabled = true
threshold = 0.95            # below this triggers a review block
budget_per_file_usd = 0.10  # skip if estimated cost exceeds cap
model = "claude-sonnet-4-6" # haiku is ~1/3 the cost
```

The judge is best-effort. Missing `attune-rag[claude]`, missing
`ANTHROPIC_API_KEY`, over-budget cost estimates, and transient
API failures all degrade silently rather than blocking the
polish. Set `block_polish_on_unavailable = true` in CI lanes
where missing deps should fail loudly instead.

End-of-run telemetry (call count, skip count, total estimated
USD) logs at INFO level after `attune-author regenerate`. Set
`ATTUNE_AUTHOR_FAITHFULNESS=off` to disable for a single run.

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
