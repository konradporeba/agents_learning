.PHONY: up down test lint fmt

COMPOSE_FILE := deploy/compose/docker-compose.yml
COMPOSE_FLAGS := -f $(COMPOSE_FILE)
ifneq ($(wildcard .env),)
COMPOSE_FLAGS += --env-file .env
endif
PNPM_VERSION := 12.18.0
PNPM := web/node_modules/.bin/pnpm

up:
	docker compose $(COMPOSE_FLAGS) up -d --wait

down:
	docker compose $(COMPOSE_FLAGS) down --remove-orphans

test: $(PNPM)
	uv run --directory backend pytest
	cd web && ./node_modules/.bin/pnpm test

lint: $(PNPM)
	uv run --directory backend ruff check .
	uv run --directory backend mypy
	cd web && ./node_modules/.bin/pnpm lint

fmt: $(PNPM)
	uv run --directory backend ruff format .
	uv run --directory backend ruff check --fix .
	cd web && ./node_modules/.bin/pnpm exec eslint . --fix

$(PNPM):
	npm install --prefix web --no-save --no-package-lock pnpm@$(PNPM_VERSION)
	cd web && ./node_modules/.bin/pnpm install
