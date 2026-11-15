# Phase 01: Foundations

[← Master plan](README.md) · Previous: [Project brief](00-project-brief.md) · Next: [02 Backend core →](02-backend-core.md)

**Estimated effort:** 8–10 hours · **Depends on:** nothing

## Outcome

A repository with working tooling, local dependencies in Docker Compose, a CI workflow that runs on every pull request, and a `labs/` folder where you have exercised every basic LLM mechanism by hand with no framework.

## Concepts

- **Tokens and context windows**: how text becomes tokens, input versus output tokens, why both cost money, what happens at the limit.
- **Chat message roles**: system, user, assistant, tool. The model is stateless; you resend the conversation every call.
- **Sampling parameters**: temperature and why "temperature 0" still does not guarantee identical output.
- **Streaming**: server-sent chunks, time to first token versus total latency.
- **Tool calling**: the model does not run tools. It returns a structured request; your code runs the tool and sends the result back.
- **Structured output**: constraining a response to a JSON schema, and what to do when validation fails.
- **Embeddings**: text to vector, cosine similarity, what "semantic similarity" does and does not capture.
- **Prompt caching**: why a stable prompt prefix is cheaper and faster.
- **Rate limits and retries**: requests per minute, tokens per minute, backoff.

## Build steps

### Repository and tooling

- [x] `git init`, create the layout from the [project brief](00-project-brief.md#repository-layout), add `.gitignore`, `.editorconfig`, a root `README.md`.
- [x] Backend tooling: `uv` for dependencies and virtualenv, `ruff` for lint and format, a type checker (`mypy` or `pyright`), `pytest`.
- [x] Frontend tooling: `pnpm`, a Vite React TypeScript skeleton in `web/`, ESLint, Vitest.
- [x] `pre-commit` hooks for format, lint and a secret scanner such as `gitleaks`.
- [x] `docs/adr/0000-template.md` and your first ADR: which LLM provider and models you will use and why.
- [x] A `Makefile` or `justfile` with `up`, `down`, `test`, `lint`, `fmt`.

### Local dependencies

- [x] `deploy/compose/docker-compose.yml` with Postgres (use an image that includes pgvector), Redis and MongoDB, each with a healthcheck and a named volume.
- [x] Configuration through `pydantic-settings` reading environment variables; commit `.env.example`, never `.env`.

### First CI

- [x] `.github/workflows/ci.yml`: on pull request, run lint, type check and unit tests for `backend/` and `web/` as separate jobs with dependency caching.
- [x] Protect `main`: require the CI checks and a pull request, even though you are working alone. You are practising the workflow.

### LLM lab (raw provider SDK, no LangChain yet)

Write each as a small script in `labs/` and keep notes on what you observed.

- [x] **Chat call**: send a system and user message, print the response and the token usage, compute the cost from the price list.
- [x] **Statelessness**: ask a follow-up question without resending history and see it fail; then resend history.
- [ ] **Streaming**: stream a response, measure time to first token and tokens per second.
- [ ] **Structured output**: parse a response into a Pydantic model. Then make validation fail on purpose and implement one retry that feeds the validation error back.
- [ ] **Tool loop by hand**: define two Python functions as tools, loop "call model → run requested tools → append results" until the model stops asking for tools, with a maximum iteration cap. This 50-line loop is the core of every agent framework.
- [ ] **Embeddings**: embed 20 sentences, compute cosine similarity with NumPy, find a pair that is semantically close but shares no words, and a pair that shares words but means something different.
- [ ] **Limits**: count tokens for a long input, exceed the context window on purpose, and read the error. Trigger a rate limit and implement exponential backoff with jitter.
- [ ] **Non-determinism**: send the same prompt 10 times at temperature 0 and at 1 and compare.

## Break it on purpose

- Commit a fake API key and confirm the pre-commit secret scanner blocks it.
- Open a pull request with a lint error and confirm it cannot be merged.
- In the tool loop, make a tool raise an exception. Decide what the model should see, and observe how it reacts to a clear error message versus a stack trace.

## Definition of done

- [ ] `make up` brings all three stores to healthy; `make down` leaves no orphans.
- [ ] A pull request shows green checks and `main` is protected.
- [ ] All lab scripts run, and `labs/NOTES.md` records what you measured.
- [ ] A spending limit is set on the LLM provider account.
- [ ] You can draw the tool-calling loop on paper, including which side executes the tool.

## Be able to explain

- Why does a long conversation get more expensive with every turn?
- What exactly does the model return when it "calls a tool", and who executes it?
- Why is temperature 0 not a guarantee of reproducible output, and what does that mean for testing?
- What is the difference between time to first token and total latency, and which matters for a chat UI?
- What does an embedding capture, and name one case where cosine similarity misleads you.

## Resources

- [uv documentation](https://docs.astral.sh/uv/)
- [The Twelve-Factor App](https://12factor.net/) (config, logs, disposability)
- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) (Anthropic): read now, reread after Phase 08
- Your chosen provider's API reference for chat, tool use, structured output and embeddings
