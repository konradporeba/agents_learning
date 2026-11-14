# Triage Copilot

A chat assistant for an engineering team: answers from project docs with citations, triage of failed CI runs, GitHub issues created only after approval, and memory across conversations.

The build plan is in [`learning_plan/`](learning_plan/README.md).

## Prerequisites

- [uv](https://docs.astral.sh/uv/)
- Node `22.21.1` from [nvm](https://github.com/nvm-sh/nvm). `.nvmrc` pins it: `nvm use`
- Docker, once the Compose file exists

pnpm is a dev dependency of `web/`. It lives in `web/node_modules` and is not installed globally. npm, which comes with Node, only bootstraps that binary. `web/pnpm-workspace.yaml` allows the `pnpm` package's install script: pnpm 12 skips dependency builds unless they are listed, and without that script the install fails.

```sh
npm install --prefix web --no-save --no-package-lock pnpm@12.18.0
cd web && ./node_modules/.bin/pnpm install
```

`make test`, `make lint`, and `make fmt` run this when `web/node_modules/.bin/pnpm` is missing.

## Backend

```sh
uv sync --directory backend
```

The project targets Python 3.12. Ruff lints and formats, mypy type-checks in strict mode, and pytest runs the tests. All three are dev dependencies.

## Make targets

| Target | Runs |
| --- | --- |
| `make up` / `make down` | `deploy/compose/docker-compose.yml` |
| `make test` | pytest, then Vitest |
| `make lint` | ruff, mypy, ESLint |
| `make fmt` | ruff format, ruff `--fix`, ESLint `--fix` |

`make up` and `make down` need the Compose file from the next foundations step.

## Git hooks

```sh
uv run --project backend pre-commit install
```

The hooks format and lint Python with ruff, type-check with mypy, lint `web/` with ESLint, and block staged secrets with gitleaks.
