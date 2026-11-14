# Agentic AI learning plan: Triage Copilot

One pet project, built end to end, that takes you from "senior SDET" to "can design, build, evaluate, ship and operate an agentic AI application".

Start with the [project brief](00-project-brief.md), then work through the phases in order.

## The project in one paragraph

**Triage Copilot** is a chat assistant for an engineering team. It answers questions about project docs with citations (RAG), investigates failed CI runs by reading GitHub Actions logs through tools, classifies each failure (product bug, test bug, flaky, infrastructure), drafts a GitHub issue and waits for a human to approve it, and remembers user preferences and past triage outcomes across conversations. The chat runs over WebSockets from a React frontend to a FastAPI backend that drives LangGraph agents.

## Why this project and not a generic chatbot

- **You already know the domain.** You can judge whether a triage answer is right without learning a new field, so your attention goes to the agent engineering.
- **You get ground truth for free.** You will build a small test suite that fails on purpose in known ways, so every CI failure has a correct label. That makes real evals possible, which most portfolio projects skip.
- **The input is untrusted.** CI logs and docs are attacker-controllable text, so prompt injection is a real problem here and not a slide in a talk.
- **It plays to your strength.** Evals, test strategy, CI/CD and load testing are where most AI engineers are weakest and where you have 8 years of experience. Phase 09 is the one that should make your CV stand out.

## Phases

| # | Phase | Main topics | Est. hours | Done |
|---|-------|-------------|-----------:|:----:|
| 00 | [Project brief](00-project-brief.md) | Product scope, architecture, data ownership, repo layout, cost | read | ☐ |
| | **Stage A: application foundation** | | | |
| 01 | [Foundations](01-foundations.md) | Repo and tooling, Docker Compose, first CI, LLM fundamentals by hand | 8–10 | ☐ |
| 02 | [Backend core](02-backend-core.md) | FastAPI, Postgres, Alembic, auth, MongoDB, integration tests | 12–15 | ☐ |
| 03 | [Realtime chat](03-realtime-chat.md) | WebSockets, Redis Streams, rate limiting, React chat UI | 15–18 | ☐ |
| | **Stage B: agentic core** | | | |
| 04 | [First agent](04-first-agent.md) | LangChain, LangGraph state and graphs, tools, checkpointing, streaming | 18–22 | ☐ |
| 05 | [LLM observability](05-llm-observability.md) | Langfuse tracing, cost, prompt management, feedback scores | 8–10 | ☐ |
| 06 | [RAG](06-rag.md) | Ingestion, chunking, pgvector, hybrid search, reranking, citations | 25–30 | ☐ |
| 07 | [Context and memory](07-context-and-memory.md) | Context budgeting, summarisation, short and long-term memory | 18–22 | ☐ |
| 08 | [Multi-agent, human-in-the-loop, MCP](08-multi-agent-hitl-mcp.md) | Routing, subgraphs, interrupts, side effects, MCP server | 25–30 | ☐ |
| | **Stage C: quality and safety** | | | |
| 09 | [Evals and testing](09-evals-and-testing.md) | Error analysis, datasets, LLM judges, CI eval gates, E2E, load tests | 25–30 | ☐ |
| 10 | [Guardrails and security](10-guardrails-security.md) | Prompt injection, tool permissions, PII, budgets, red teaming | 10–12 | ☐ |
| | **Stage D: ship and operate** | | | |
| 11 | [CI pipeline](11-ci-pipeline.md) | Pipeline design, images, scanning, signing, OIDC, release flow | 10–12 | ☐ |
| 12 | [Kubernetes locally](12-kubernetes-local.md) | Helm, probes, Gateway API, autoscaling, debugging drills on kind | 15–18 | ☐ |
| 13 | [Cloud with Terraform](13-cloud-terraform.md) | Azure, AKS, managed Postgres, Key Vault, workload identity, state | 18–22 | ☐ |
| 14 | [CD, rollbacks, migrations](14-cd-rollbacks-migrations.md) | GitOps, canary, rollback drills, expand/contract, prompt and model rollout | 18–22 | ☐ |
| 15 | [Monitoring and operations](15-monitoring-operations.md) | OpenTelemetry, Prometheus, Grafana, SLOs, alerts, runbooks | 15–18 | ☐ |
| | **Stage E: capstone** | | | |
| 16 | [Capstone and job prep](16-capstone-job-prep.md) | Portfolio polish, write-ups, interview bank, stretch topics | 10–12 | ☐ |

The hour figures are my rough estimates for someone with your background, not measurements. The total is about 250–300 hours: roughly 5–6 months at 12 hours a week, or about 3 months at 20–25.

## Where each topic you asked for is covered

| Topic | Phase |
|-------|-------|
| LangChain, LangGraph | [04](04-first-agent.md), [07](07-context-and-memory.md), [08](08-multi-agent-hitl-mcp.md) |
| Langfuse | [05](05-llm-observability.md), [09](09-evals-and-testing.md), [14](14-cd-rollbacks-migrations.md) |
| Context management | [07](07-context-and-memory.md) |
| Memory management | [07](07-context-and-memory.md) |
| RAG | [06](06-rag.md) |
| Model and agent evals | [09](09-evals-and-testing.md) |
| Testing (unit, integration, E2E, performance) | [02](02-backend-core.md), [03](03-realtime-chat.md), [09](09-evals-and-testing.md) |
| Continuous integration | [01](01-foundations.md), [11](11-ci-pipeline.md) |
| Deployment pipelines, rollbacks, migrations | [14](14-cd-rollbacks-migrations.md) |
| Kubernetes | [12](12-kubernetes-local.md), [13](13-cloud-terraform.md) |
| Cloud and Terraform | [13](13-cloud-terraform.md) |
| Monitoring | [05](05-llm-observability.md), [15](15-monitoring-operations.md) |
| React frontend | [03](03-realtime-chat.md), then extended in 04–08 |
| FastAPI | [02](02-backend-core.md) |
| Postgres | [02](02-backend-core.md), [06](06-rag.md), [14](14-cd-rollbacks-migrations.md) |
| NoSQL (MongoDB) | [02](02-backend-core.md), [06](06-rag.md), [08](08-multi-agent-hitl-mcp.md) |
| Redis | [03](03-realtime-chat.md), [06](06-rag.md) |
| WebSockets | [03](03-realtime-chat.md), [04](04-first-agent.md), [12](12-kubernetes-local.md) |

## How every phase file is laid out

- **Outcome**: what exists and works when you finish.
- **Concepts**: what to read about before and during the build.
- **Build steps**: a checklist, in order.
- **Break it on purpose**: failure drills. Do not skip these; they are where most of the understanding comes from.
- **Definition of done**: checks you can verify, not feelings.
- **Be able to explain**: interview-style questions. Answer them out loud or in writing.
- **Resources**: official docs and a few articles worth the time.

## Working rules

1. **Write the agent code yourself.** Use an AI assistant as a reviewer and tutor for phases 04–10: ask it to explain, critique, and quiz you. Let it generate boilerplate (Dockerfiles, React forms, Helm scaffolding) where you already know what good looks like.
2. **Hand-build before you use the prebuilt.** Each phase has you write the raw version first (a tool loop, a retrieval function, a metric) and then switch to the library. You need this to debug the library later.
3. **Keep an engineering log.** One ADR in `docs/adr/` per real decision, plus a short `docs/journal.md` entry per session: what you built, what broke, what surprised you. This becomes your interview material.
4. **Trace first, then change.** From Phase 05 onward, look at the Langfuse trace before you change a prompt. From Phase 09 onward, run the evals before and after.
5. **Finish the definition of done before moving on.** A shallow pass over all 16 phases is worth less than a deep pass over 10.
6. **Put a hard spending cap on your LLM provider account on day one**, and use the fake LLM mode (Phase 03) for everything that does not need a real model.

## Checkpoints

- **After Phase 05**: you have a working, traced, tool-using agent with a real UI. Start reading job descriptions and note which terms you cannot yet explain.
- **After Phase 09**: the AI-specific part is complete. This is a reasonable point to start applying while you continue with Stage D, where your existing experience lets you move faster.
- **After Phase 15**: you can tell the whole story from prompt change to production rollback.

## A note on versions

This ecosystem changes quickly. When this plan was written (14 November 2026) LangGraph was at 1.2.x, LangChain's agent entry point was `create_agent` with middleware, and Langfuse was at v4. The plan teaches concepts and names APIs only as pointers. At the start of each phase, open the current docs and check that the API names still match.
