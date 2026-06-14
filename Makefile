.PHONY: setup install test lint status regenerate clean help sync-hooks

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Configure git hooks and install in dev mode
	git config core.hooksPath .githooks
	uv pip install -e ".[dev]"
	@echo "\n✓ Hooks active, dev deps installed"

install: ## Install package in dev mode
	uv pip install -e ".[dev]"

test: ## Run test suite
	uv run pytest

lint: ## Run ruff linter
	uv run ruff check src/ tests/

status: ## Check help template staleness
	uv run attune-author status

regenerate: ## Regenerate all help templates
	uv run python scripts/regenerate_help.py

eval: ## Full RAG hallucination benchmark (25 questions, 2 models — costs ~$3-8 in API calls)
	cd benchmarks/hallucination-v0.3.9 && uv run python run_answers.py && uv run python run_judge.py && uv run python report.py

eval-smoke: ## Smoke RAG gate check (5 questions, 1 model — costs ~$0.10-0.30 in API calls)
	uv run python benchmarks/smoke_eval.py

clean: ## Remove build artifacts
	rm -rf build/ dist/ *.egg-info src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

ATTUNE_AI_ROOT ?= ../attune-ai
HOOK_FILES = security_guard.py format_on_save.py compact_warning.py spec_orient.py _state.py _resume_prompt.py _transcript_size.py

sync-hooks:  ## Re-copy session hooks from attune-ai canonical + refresh checksums.
	@if [ ! -d "$(ATTUNE_AI_ROOT)/plugin/hooks" ]; then \
		echo "Error: $(ATTUNE_AI_ROOT)/plugin/hooks not found. Set ATTUNE_AI_ROOT=<path>"; \
		exit 1; \
	fi
	@mkdir -p .claude/hooks
	@for f in $(HOOK_FILES); do \
		cp "$(ATTUNE_AI_ROOT)/plugin/hooks/$$f" ".claude/hooks/$$f"; \
		echo "  synced: $$f"; \
	done
	@(cd .claude/hooks && shasum -a 256 $(HOOK_FILES) > .canonical-sha256)
	@echo "✓ .claude/hooks/.canonical-sha256 refreshed"
