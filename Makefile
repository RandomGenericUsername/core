MAKEFLAGS += --no-print-directory

# All workspace packages in dependency order
PACKAGES := logging pipeline package-manager container-manager

.PHONY: help sync install dev-shell format lint type-check \
        test test-cov \
        test-logging test-pipeline test-package-manager test-container-manager \
        clean clean-venv pre-commit-install pre-commit-run all-checks

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-28s %s\n", $$1, $$2}'

# ─── Workspace sync ─────────────────────────────────────────────────────────

sync: ## Sync entire workspace (installs all packages into shared .venv)
	@echo "Syncing workspace..."
	@uv sync
	@echo "✅ Workspace sync complete"

install: ## Alias for sync
	@$(MAKE) sync

dev-shell: ## Activate the shared workspace virtual environment
	@echo "Activating virtual environment..."
	@echo "Leave the dev shell by typing 'exit'"
	@bash -c "source .venv/bin/activate && exec bash"

# ─── Code quality (workspace-wide) ──────────────────────────────────────────

format: ## Format all packages with black and isort
	@echo "Formatting all packages..."
	@uv run black packages/
	@uv run isort packages/
	@echo "✅ Formatting complete"

lint: ## Lint all packages with ruff
	@echo "Linting all packages..."
	@uv run ruff check --fix packages/
	@echo "✅ Linting complete"

type-check: ## Type check each package with mypy (delegated per-package)
	@echo "Type checking all packages..."
	@for pkg in $(PACKAGES); do \
		echo ""; \
		echo "--- $$pkg ---"; \
		$(MAKE) -C packages/$$pkg type-check; \
	done
	@echo ""
	@echo "✅ Type checking complete"

# ─── Tests (must run per-package — workspace-wide run causes namespace collision) ──

test: ## Run tests for all packages (each package run independently)
	@echo "Running all tests..."
	@for pkg in $(PACKAGES); do \
		echo ""; \
		echo "--- Testing $$pkg ---"; \
		$(MAKE) -C packages/$$pkg test; \
	done
	@echo ""
	@echo "✅ All tests complete"

test-cov: ## Run tests with coverage for all packages
	@echo "Running all tests with coverage..."
	@for pkg in $(PACKAGES); do \
		echo ""; \
		echo "--- Testing $$pkg (with coverage) ---"; \
		$(MAKE) -C packages/$$pkg test-cov; \
	done
	@echo ""
	@echo "✅ Coverage complete"

test-logging: ## Run tests for the logging package only
	@$(MAKE) -C packages/logging test

test-pipeline: ## Run tests for the pipeline package only
	@$(MAKE) -C packages/pipeline test

test-package-manager: ## Run tests for the package-manager package only
	@$(MAKE) -C packages/package-manager test

test-container-manager: ## Run tests for the container-manager package only
	@$(MAKE) -C packages/container-manager test

# ─── Cleanup ─────────────────────────────────────────────────────────────────

clean: ## Clean cache files and build artifacts across all packages
	@echo "Cleaning all packages..."
	@for pkg in $(PACKAGES); do \
		$(MAKE) -C packages/$$pkg clean; \
	done
	@find . -maxdepth 2 -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -maxdepth 2 -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -maxdepth 1 -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -maxdepth 1 -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -maxdepth 1 -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup complete"

clean-venv: ## Remove the shared workspace virtual environment
	@echo "Removing virtual environment..."
	@rm -rf .venv
	@echo "✅ Virtual environment removed"
	@echo "Run 'make sync' to recreate"

# ─── Pre-commit ───────────────────────────────────────────────────────────────

pre-commit-install: ## Install pre-commit hooks
	@echo "Installing pre-commit hooks..."
	@uv run pre-commit install
	@echo "✅ Pre-commit hooks installed"

pre-commit-run: ## Run pre-commit on all files
	@echo "Running pre-commit on all files..."
	@uv run pre-commit run --all-files
	@echo "✅ Pre-commit checks complete"

# ─── Composite ────────────────────────────────────────────────────────────────

all-checks: format lint type-check test ## Run all checks (format, lint, type-check, test)
	@echo "✅ All checks passed!"
