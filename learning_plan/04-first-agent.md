# Phase 04: First agent

[← Master plan](README.md) · Previous: [03 Realtime chat](03-realtime-chat.md) · Next: [05 LLM observability →](05-llm-observability.md)

**Estimated effort:** 18–22 hours · **Depends on:** Phase 03

## Outcome

A real LLM agent replaces the fake streamer. It can call read-only GitHub tools to inspect workflow runs, its conversation state is checkpointed in Postgres so it survives restarts, and its tokens and tool activity stream to the UI through the protocol you built in Phase 03.

## Concepts

### Agents in general

- **Workflow versus agent**: a workflow follows a path you wrote; an agent lets the model choose the next step. Most production systems are mostly workflow with agentic parts.
- **Tool design**: the name, description and argument schema are a prompt. Error messages returned to the model are also a prompt.
- **Loop control**: iteration caps, timeouts, cost budgets.

### LangChain

- Chat model abstraction and provider-agnostic initialisation, message types, tool definitions, structured output.
- `create_agent` and **middleware**: the prebuilt tool-calling loop and the hooks that customise it.

### LangGraph

- **State**: a typed schema shared by all nodes; **reducers** decide how updates merge (appending messages versus overwriting a field).
- **Nodes and edges**: functions that return state updates; fixed and conditional edges; super-steps.
- **Checkpointer and threads**: state saved after every step under a `thread_id`; this is short-term memory and also what makes a run resumable.
- **Streaming modes**: full state values, per-node updates, LLM token messages, custom events.
- **Durable execution**: what is replayed after a crash, and why nodes with side effects need care.
- **Time travel**: reading state history and forking from an earlier checkpoint.
- **Recursion limit**: the built-in guard against infinite loops.

## Build steps

### Hand-build, then use the prebuilt

- [ ] Port the hand-written tool loop from `labs/` to a hand-built `StateGraph`: a model node, a tool node, and a conditional edge that routes on "did the model request tools". Export the graph diagram and put it in the docs.
- [ ] Build the same agent with `create_agent`. Compare the two graphs and their state.
- [ ] ADR: which approach the product uses and why. A reasonable default is `create_agent` for standard tool loops and hand-built graphs where you need explicit control flow (Phase 08).

### Tools, version 1 (read-only GitHub)

- [ ] A fine-grained personal access token with read-only access to this repository's Actions and metadata. Nothing more.
- [ ] Tools: `list_workflow_runs`, `get_run_summary`, `list_failed_jobs`, `get_job_log_excerpt`.
- [ ] Each tool has typed arguments, a description written for the model, a timeout, and returns a short useful message on failure.
- [ ] `get_job_log_excerpt` must never return a whole log. Return the failing section plus a line count. You will formalise this in Phase 07.
- [ ] Make one of your own CI runs fail on purpose so the agent has something to investigate.

### Model configuration

- [ ] One place that builds the model from settings: provider, model name, temperature, timeout, retries, and a fallback model.
- [ ] A system prompt in a file under version control (it moves to Langfuse in Phase 05).

### Persistence

- [ ] The async Postgres checkpointer, with `thread_id` equal to the conversation ID. Look at the tables it creates.
- [ ] Restart the API mid-conversation and continue it.
- [ ] ADR: the message transcript in your `messages` table versus the checkpoint. Which one renders history in the UI, which one the agent reads, and what keeps them consistent.

### Streaming bridge

- [ ] Implement the Phase 03 streamer interface with a real graph run: map LLM token chunks to `token` events and tool activity to `tool.started` and `tool.finished`.
- [ ] Wire `run.cancel` to cancel the graph run.
- [ ] UI: a collapsible tool timeline under each assistant message showing tool name, arguments, duration and a result preview.

### Tests

- [ ] Tools: unit tests with mocked HTTP (success, 404, rate limited, timeout).
- [ ] Graph: tests with a **scripted fake chat model** that returns a predetermined sequence of tool calls and answers. Assert routing, state, and the emitted WebSocket events. These are deterministic and run on every pull request.
- [ ] A test that the recursion limit stops a model that always requests another tool call.
- [ ] Keep the fake streamer mode working; your Phase 03 E2E tests should still pass unchanged.

### Explore

- [ ] Read the state history of a thread, pick an earlier checkpoint, change the user message, and fork from there.

## Break it on purpose

- A tool raises an unexpected exception. What does the model see? What does the user see?
- A tool returns 2 MB of log text. Watch the token count and cost in the response metadata.
- Write a deliberately vague tool description and watch the model misuse the tool. Then fix the description, not the system prompt.
- Kill the process while a tool is executing, restart, and resume the thread. Note which step ran again.
- Point the agent at the fallback model by making the primary time out.

## Definition of done

- [ ] "Why did the last CI run fail?" produces an answer grounded in real log lines, with the tool calls visible in the UI.
- [ ] A conversation continues correctly after an API restart.
- [ ] Deterministic graph tests run in CI with no network and no API key.
- [ ] The hand-built graph and the `create_agent` version both exist, and you can explain every node in each.
- [ ] No tool can return unbounded output.

## Be able to explain

- What is a reducer, and what goes wrong if the messages field uses overwrite instead of append?
- What exactly does a checkpointer store, and when? How is that different from long-term memory?
- If the process dies after a tool ran but before the next checkpoint, what happens on resume? What does that imply for tools with side effects?
- How do you unit test an agent without calling a model?
- When would you choose a fixed workflow over an agent?

## Resources

- [LangChain and LangGraph documentation](https://docs.langchain.com/)
- [LangChain middleware overview](https://docs.langchain.com/oss/python/langchain/middleware/overview)
- [LangGraph memory and persistence](https://docs.langchain.com/oss/python/langgraph/add-memory)
- [GitHub REST API: Actions](https://docs.github.com/en/rest/actions)
