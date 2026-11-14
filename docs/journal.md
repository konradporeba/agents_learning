# Engineering journal

Newest entry first. One entry per work day.

## 2026-11-14

**Phase:** 01
**Built:** Wrote the Triage Copilot learning plan in `learning_plan/` (brief plus 16 phases). Turned the six working rules into always-apply Cursor project rules in `.cursor/rules/`. Added the `write-adr` and `write-journal` skills in `.cursor/skills/` so the same agent writes `docs/adr/` and this journal. I first called these agents; skills fit, because both are workflows for the agent already in the repo, not separate ones. Whether a new chat actually loads the rules is not verified. Scaffolded the repo layout and tooling: uv project in `backend/` (Python 3.12, ruff 0.17.5, mypy 2.4.1 strict, pytest 9.2.0), Vite React TypeScript app in `web/` with ESLint and Vitest, pnpm 12.18.0 as a local dev dependency, pre-commit with ruff, mypy, ESLint, and gitleaks 8.30.1, plus a Makefile. `make test` and `make lint` passed. `make up` / `make down` are wired to a Compose file that does not exist yet. Accepted ADR 0002: OpenRouter is the provider, and the development, production, and eval model ids are still unset. Ticked the six repository-and-tooling boxes in `learning_plan/01-foundations.md`. Added `learning_plan/PROGRESS.md` from the phase checklists: 6 of 482 items checked.
**Broke:** The first `pnpm install` exited with `ERR_PNPM_IGNORED_BUILDS` for the `pnpm` package itself. pnpm 12 no longer reads a `pnpm` key in `package.json`. Allowing `pnpm: true` under `allowBuilds` in `web/pnpm-workspace.yaml` let the install script run, and the install then exited 0.
**Surprised:** The local `web/node_modules/.bin/pnpm` shim still printed `12.18.0` before that build was allowed. The install only became a clean exit after the allow-list.
**Next:** Local Postgres, Redis, and MongoDB in Docker Compose. Model tiers on OpenRouter are not chosen. No spending cap has been confirmed.
