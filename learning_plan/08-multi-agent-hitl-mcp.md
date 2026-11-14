# Phase 08: Multi-agent, human-in-the-loop, MCP

[← Master plan](README.md) · Previous: [07 Context and memory](07-context-and-memory.md) · Next: [09 Evals and testing →](09-evals-and-testing.md)

**Estimated effort:** 25–30 hours · **Depends on:** Phase 07

## Outcome

The full product: a router sends each request to a docs agent, a triage agent or an action agent. The triage agent analyses several failures in parallel and classifies them with structured output. Creating a GitHub issue pauses the run until the user approves it in the UI. Your own MCP server exposes CI failure history, and a sample app generates labelled failures on demand.

## Concepts

- **Multi-agent patterns**: router, supervisor with workers, handoffs between peers, agents as tools. What each costs in tokens, latency and debuggability.
- **When not to use multiple agents**: one agent with good tools is simpler and often better. Split when contexts, tools or permissions differ.
- **Subgraphs**: composing graphs, state mapping between parent and child, how checkpointing and streaming work across the boundary.
- **Control flow primitives**: conditional edges, `Command` for combined state update and routing, `Send` for fan-out and map-reduce.
- **Human-in-the-loop**: `interrupt` pauses a run and persists it; `Command(resume=...)` continues it, possibly hours later and on another pod. Approve, edit and reject patterns.
- **Side effects and idempotency**: on resume, the interrupted node runs again from its start. Anything before the interrupt in that node repeats.
- **Model Context Protocol (MCP)**: servers expose tools, resources and prompts; transports (stdio, streamable HTTP); why a standard protocol matters.
- **Reliability**: per-node retries and timeouts, fallbacks, partial failure in parallel branches, budget limits per run.

## Build steps

### Labelled failure generator

- [ ] `flaky-shop/`: a tiny API with a pytest and Playwright suite, and a `FAIL_MODE` switch that injects one of four behaviours: a real product bug, a broken test (bad selector or assertion), a timing-dependent flaky test, and an infrastructure fault (dependency unavailable).
- [ ] A `workflow_dispatch` workflow that runs the suite with a chosen mode and uploads JUnit XML and logs as artifacts.
- [ ] Trigger it 20–30 times across modes. Record run ID and true label in `evals/datasets/triage_labeled.jsonl`. This is your ground truth for Phase 09.

### Triage agent

- [ ] Tools: download and parse JUnit artifacts; fetch log sections (reuse offloading from Phase 07); `find_similar_failures` over episodic memory and failure records.
- [ ] Store parsed failure records in MongoDB and their signatures as embeddings in Postgres.
- [ ] Classification as structured output: category, confidence, evidence (quoted log lines), suggested next step.
- [ ] Fan-out with `Send`: one branch per failed test, then a reduce step that groups related failures and writes the summary.
- [ ] Handle partial failure: one branch erroring must not lose the others.

### Routing and composition

- [ ] A parent graph with a router node (structured output: `docs`, `triage`, `action`, `chat`) and the three agents as subgraphs.
- [ ] Decide how much conversation history each subgraph receives. The triage agent does not need the docs agent's retrieved chunks.
- [ ] Stream events from subgraphs through to the UI, labelled with the agent name.
- [ ] ADR: why this is a router and not a supervisor loop, and what would make you change it.

### Human-in-the-loop action

- [ ] A second GitHub token that can create issues, used only by the action agent. The other agents keep the read-only token.
- [ ] Action agent flow: draft issue (title, body, labels) → `interrupt` with the draft → resume with approve, edited draft, or reject → create the issue.
- [ ] Put the interrupt in its own node, before the node that calls GitHub, so resuming never repeats a side effect.
- [ ] An idempotency key on issue creation, stored in Postgres with the approval record: who approved what, and when.
- [ ] Protocol and UI: the `interrupt` event renders an approval card with an editable draft; `interrupt.resume` carries the decision.
- [ ] Pending approvals survive a page reload and an API restart.
- [ ] Compare your implementation with the built-in human-in-the-loop middleware.

### MCP

- [ ] Build `mcp-ci`: an MCP server exposing `search_failures`, `get_failure`, and `failure_stats` over your MongoDB failure records. Read-only.
- [ ] Connect the triage agent to it through the LangChain MCP adapters, over HTTP transport, with authentication.
- [ ] Connect the same server to your IDE's agent and query your failure history from there. This shows why the protocol is useful.
- [ ] Optional: replace your hand-written GitHub tools with GitHub's MCP server and compare tool quality, token cost and control.

### Run isolation

- [ ] Per-run limits: maximum steps, maximum tool calls, maximum cost. Exceeding one ends the run with a clear message.
- [ ] Optional but valuable: move graph execution from the API process to the worker, with the API only reading the Redis Stream. Decide based on what happened in the Phase 03 "kill a replica" drill now that runs are long.

### Tests

- [ ] Router tests with the scripted fake model, one per route.
- [ ] Interrupt tests: run to the interrupt, assert no issue was created, resume with each of approve, edit, reject.
- [ ] A test that resuming twice with the same decision creates one issue.
- [ ] Contract tests for the MCP server's tool schemas.
- [ ] Playwright E2E for the approval journey in fake-LLM mode.

## Break it on purpose

- Put the GitHub call in the same node as the interrupt, above it or below it, and observe what repeats on resume.
- Approve an issue from two browser tabs at the same moment.
- Restart the API while a run is waiting for approval, then approve.
- Make one parallel triage branch time out.
- Give the router an ambiguous request ("the checkout docs test is failing") and inspect the trace.
- Stop the MCP server mid-run.

## Definition of done

- [ ] All four user journeys from the [brief](00-project-brief.md#what-the-product-does) work end to end in the UI.
- [ ] No code path creates an issue without a recorded approval (test-enforced).
- [ ] Triage of a run with several failures executes in parallel, visible in the trace.
- [ ] The MCP server is used by both your agent and an external client.
- [ ] `triage_labeled.jsonl` has at least 20 labelled runs across all four categories.
- [ ] Per-run step and cost limits are enforced.

## Be able to explain

- Compare router, supervisor and handoff patterns. Which did you choose and why?
- When is a multi-agent design worse than a single agent?
- What happens, step by step, when a run hits an interrupt and is resumed the next day?
- How do you make a tool with side effects safe under retries and resumes?
- What problem does MCP solve, and what new risks does connecting a third-party MCP server introduce?
- How do you limit the blast radius of an agent that has write access to an external system?

## Resources

- [LangGraph documentation](https://docs.langchain.com/) (subgraphs, interrupts, `Send`, `Command`)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [LangChain MCP adapters](https://github.com/langchain-ai/langchain-mcp-adapters)
- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) (reread: patterns section)
