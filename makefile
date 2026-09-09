PYTHON ?= uv run
COMPOSE_DEV ?= docker compose -f docker-compose.dev.yml

.PHONY: install
install: ## Install all dependencies
	uv sync --all-groups

.PHONY: sync
sync: ## Sync runtime dependencies
	uv sync --frozen --no-dev

.PHONY: lock
lock: ## Refresh uv.lock
	uv lock

.PHONY: upgrade
upgrade: ## Apply Alembic migrations
	$(PYTHON) alembic upgrade head

.PHONY: downgrade
downgrade: ## Rollback last Alembic migration
	$(PYTHON) alembic downgrade -1

.PHONY: generate
generate: ## Autogenerate Alembic revision (NAME=...)
	$(PYTHON) alembic revision --autogenerate -m "$(NAME)"

.PHONY: history
history: ## Show Alembic history
	$(PYTHON) alembic history

.PHONY: run-http
run-http: ## Run HTTP API
	$(PYTHON) python -m src.entrypoints.http

.PHONY: lint
lint: ## Run ruff linter
	$(PYTHON) ruff check src tests

.PHONY: format
format: ## Format code
	$(PYTHON) ruff format src tests
	$(PYTHON) ruff check --fix src tests

.PHONY: typecheck
typecheck: ## Run mypy
	$(PYTHON) mypy src

.PHONY: check
check: lint typecheck ## Run static checks

.PHONY: test
test: ## Run all tests
	$(PYTHON) pytest

.PHONY: test-unit
test-unit: ## Run unit tests
	$(PYTHON) pytest -m unit

.PHONY: docker-dev-up
docker-dev-up: ## Start dev infra
	$(COMPOSE_DEV) up -d

.PHONY: run-worker
run-worker: ## Run Taskiq worker
	$(PYTHON) taskiq worker src.entrypoints.tasks:broker
