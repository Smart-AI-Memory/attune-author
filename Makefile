.PHONY: setup install test lint status regenerate clean help

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

clean: ## Remove build artifacts
	rm -rf build/ dist/ *.egg-info src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
