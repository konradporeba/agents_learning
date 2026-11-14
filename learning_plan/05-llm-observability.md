# Phase 05: LLM observability with Langfuse

[← Master plan](README.md) · Previous: [04 First agent](04-first-agent.md) · Next: [06 RAG →](06-rag.md)

**Estimated effort:** 8–10 hours · **Depends on:** Phase 04

## Outcome

Every agent run produces a trace in Langfuse showing each model call, tool call, token count and cost, grouped by user and conversation. Prompts are versioned in Langfuse and fetched at runtime. A thumbs up or down in the UI becomes a score on the trace.

This phase comes early on purpose. From here on, you look at traces before you change anything.

## Concepts

- **Trace structure**: a trace per run; nested observations (spans for steps, generations for model calls); sessions group traces into a conversation; users, tags, metadata, environment and release.
- **Cost tracking**: token usage per generation, model price tables, cost per trace and per user.
- **Prompt management**: versions, labels such as `production` and `staging`, client-side caching, linking a prompt version to the traces that used it.
- **Scores**: numeric, categorical or boolean values attached to a trace, from users, code or an LLM judge.
- **Operational concerns**: asynchronous batching, flushing on shutdown, sampling, masking sensitive data, and never letting telemetry break a request.
- **Langfuse architecture**: web and worker containers, Postgres for transactional data, ClickHouse for traces, Redis for queue and cache, S3-compatible storage for raw events. Understanding why each exists is a good system design exercise.
- **Relationship to OpenTelemetry**: Langfuse's SDK is built on OTel. Infrastructure tracing comes in Phase 15; here the focus is the LLM layer.

## Build steps

### Run Langfuse

- [ ] Start Langfuse locally with its official Docker Compose file, as a separate Compose project. It is heavy (web, worker and four data stores), so stop it when you are not using it.
- [ ] Look at each container and write one sentence on its role. Alternative if your machine struggles: Langfuse Cloud's free tier.

### Instrument the agent

- [ ] Attach the Langfuse LangChain callback handler to graph invocations.
- [ ] Set on every trace: user ID, session ID (the conversation ID), environment, release (git SHA), and tags for the agent name.
- [ ] Wrap your own non-LangChain code (the tool HTTP calls now, retrieval later) with Langfuse spans so there are no blind spots.
- [ ] Flush on shutdown so traces are not lost when a pod terminates.

### Close the feedback loop

- [ ] Include the trace ID in the `run.completed` WebSocket event.
- [ ] Thumbs up and down buttons in the UI, with an optional comment. The backend writes the feedback to Postgres and as a score in Langfuse.

### Prompt management

- [ ] Move the system prompt into Langfuse. Fetch it by label at runtime.
- [ ] Keep the in-repository copy as a fallback for when Langfuse is unreachable.
- [ ] Link the prompt version to each trace, so you can filter traces by prompt version.
- [ ] Change the prompt in Langfuse, move the `production` label, and see the app pick it up without a deploy. Then move the label back. You have just done a prompt rollback; Phase 14 formalises it.

### Safety

- [ ] A masking function that redacts tokens, emails and anything that looks like a secret before data leaves the process.
- [ ] A test that stops Langfuse and confirms user requests still succeed.

### Use it

- [ ] A Langfuse dashboard with cost per conversation, latency p50 and p95, and tool error rate.
- [ ] Read 20 of your own traces end to end. Write down three things that surprised you (unexpected tool calls, wasted tokens, slow steps). This habit is the start of error analysis in Phase 09.

## Break it on purpose

- Stop Langfuse mid-run. Nothing user-visible should change.
- Put a fake API key in a tool result and confirm it is masked in the trace.
- Delete the `production` label from the prompt. The fallback must take over, and something must tell you it did.
- Find the most expensive trace you have produced so far and explain where the tokens went.

## Definition of done

- [ ] Every run has a trace with nested model and tool observations, cost, user and session.
- [ ] You can filter traces by prompt version and by release.
- [ ] UI feedback appears as a score on the right trace.
- [ ] Tracing failure does not affect requests (automated test).
- [ ] No secrets or tokens are visible in traces.

## Be able to explain

- What is the difference between a trace, a span and a generation?
- Why manage prompts outside the codebase, and what risks does that introduce?
- How would you find out which prompt version caused a spike in cost or bad feedback?
- Why does Langfuse use ClickHouse for traces and Postgres for everything else?
- What should happen to user requests when the observability backend is down?

## Resources

- [Langfuse documentation](https://langfuse.com/docs)
- [Langfuse self-hosting and architecture](https://langfuse.com/self-hosting)
- [Langfuse Docker Compose deployment](https://langfuse.com/self-hosting/deployment/docker-compose)
