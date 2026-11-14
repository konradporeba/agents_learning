# Phase 07: Context and memory management

[← Master plan](README.md) · Previous: [06 RAG](06-rag.md) · Next: [08 Multi-agent, HITL, MCP →](08-multi-agent-hitl-mcp.md)

**Estimated effort:** 18–22 hours · **Depends on:** Phase 06

## Outcome

Long conversations stay within a token budget without losing what matters, large tool outputs no longer flood the context, and the assistant remembers user preferences and facts across conversations. Users can see and delete what is remembered.

## Concepts

### Context engineering

The context window is a budget. Everything in it competes for the model's attention: system prompt, tool definitions, retrieved chunks, conversation history, tool results, memories.

- **Failure modes of long context**: important details get ignored, stale or wrong information persists, irrelevant content distracts, contradictory content confuses.
- **Strategies**:
  - *Trim*: drop the oldest messages, keeping tool call and result pairs intact.
  - *Summarise*: compact older turns into a running summary.
  - *Offload*: store large content outside the context and pass a reference and an excerpt.
  - *Select*: retrieve only what the current step needs (RAG, memory search, tool subsets).
  - *Isolate*: give a sub-agent its own context and return only its result (Phase 08).
- **Prompt caching**: keep the stable part of the prompt first and unchanged so providers can cache it.

### Memory

- **Short-term memory**: the thread's checkpointed state. Scoped to one conversation.
- **Long-term memory**: persists across threads, kept in a store under namespaces such as user or project.
- **Types**: *semantic* (facts and preferences), *episodic* (what happened in past interactions), *procedural* (instructions the agent has learned about how to behave).
- **Writing memories**: in the hot path (the agent calls a tool to save) versus in the background (a job extracts memories after the conversation). Trade-offs in latency, cost and quality.
- **Reading memories**: always-loaded profile versus search by relevance.
- **Hygiene**: updates and contradictions, staleness, deletion, privacy.

## Build steps

### Measure first

- [ ] A token-accounting helper that reports how the context of a model call divides between system prompt, tool definitions, memories, retrieved chunks, history and tool results. Log it to the Langfuse trace.
- [ ] Hold a 30-turn triage conversation and chart how the context grows. Find what dominates.

### Short-term context

- [ ] A configurable token budget per model call.
- [ ] Trimming that never orphans a tool result from its tool call. Write this one yourself and unit test it.
- [ ] Summarisation of older turns into a running summary held in state. Then compare with the built-in summarisation middleware.
- [ ] Confirm the UI still shows the full transcript while the agent sees the compacted one. This is the transcript-versus-checkpoint split from the [brief](00-project-brief.md#which-store-owns-what).
- [ ] Tool result offloading: store the full CI log in MongoDB, return an excerpt and a reference to the model, and add a `read_log_section` tool to fetch more on demand.
- [ ] Order the prompt so the stable prefix comes first. Check cache-hit token counts in the provider's usage data before and after.

### Long-term memory

- [ ] Add the Postgres-backed LangGraph store. Namespaces: per user for preferences, per project for facts.
- [ ] **Semantic memory**: a user profile (role, owned test areas, answer style). Loaded into every run.
- [ ] Hot-path write: a `remember` tool the agent can call when the user states a preference.
- [ ] Background write: a worker job that runs after a conversation goes idle, extracts candidate memories, and merges them with existing ones (update, not duplicate).
- [ ] **Episodic memory**: after a triage is resolved, store a short record (failure signature, classification, resolution). Retrieved by similarity in Phase 08.
- [ ] **Procedural memory**: let a user correction such as "always include the failing test name in the summary" become a stored instruction added to the system prompt for that user.
- [ ] Memory search by relevance for anything that is not always loaded.

### User control

- [ ] A "Memory" page in the UI: list what is stored about the user, edit, delete.
- [ ] `DELETE` really deletes. Add a test.
- [ ] Memories are scoped. Add cross-user and cross-project isolation tests, as you did for retrieval.

### Evaluate

- [ ] A small memory dataset: conversation A states a fact; conversation B asks something that depends on it. Assert the fact is used.
- [ ] Cases for contradiction ("I moved to the payments team") and for things that must not be stored (secrets, one-off details).
- [ ] A summarisation regression case: a detail from turn 3 must still be answerable at turn 40.

## Break it on purpose

- Turn off trimming and summarisation and keep talking until the context window overflows.
- Trim naively by message count and trigger the provider error for a tool result with no matching tool call.
- Tell the assistant two contradictory preferences in separate conversations. See what is stored.
- Paste an API key into the chat and check whether background extraction saves it.
- Summarise aggressively and ask about a detail from early in the conversation.

## Definition of done

- [ ] A 50-turn conversation stays under the budget, and the early-detail regression case passes.
- [ ] No tool result above a set size ever enters the context in full.
- [ ] A preference stated in one conversation changes behaviour in a new one.
- [ ] The memory page lists, edits and deletes; deletion is verified by a test.
- [ ] The context composition of any model call is visible in its trace.
- [ ] You have before and after numbers for tokens per turn and cache hits.

## Be able to explain

- What is the difference between a checkpointer and a store?
- Name four ways to reduce context and the risk of each.
- When would you write memories in the hot path and when in the background?
- How do you stop a long-term memory system from accumulating stale or contradictory facts?
- Why does the order of content in the prompt affect cost?
- How would you test that summarisation does not lose important information?

## Resources

- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) (Anthropic)
- [LangGraph memory](https://docs.langchain.com/oss/python/langgraph/add-memory)
- [LangChain middleware](https://docs.langchain.com/oss/python/langchain/middleware/overview) (summarisation and context editing)
- Your provider's prompt caching documentation
