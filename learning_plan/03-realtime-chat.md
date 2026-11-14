# Phase 03: Realtime chat

[← Master plan](README.md) · Previous: [02 Backend core](02-backend-core.md) · Next: [04 First agent →](04-first-agent.md)

**Estimated effort:** 15–18 hours · **Depends on:** Phase 02

## Outcome

A React chat UI that streams responses over a WebSocket. The "model" is a fake streamer that emits tokens with a delay. Two API replicas run behind a proxy, and a client connected to either one receives the stream, can cancel it, and can reconnect mid-stream without losing or duplicating events.

Building the transport against a fake model first means that when you add a real agent in Phase 04, any bug you see is an agent bug.

## Concepts

- **WebSocket lifecycle**: handshake, frames, ping and pong, close codes.
- **WebSockets versus server-sent events**: many LLM products stream with SSE because it is simpler. You use WebSockets because the client must also send mid-run messages (cancel, approve). Be able to argue both sides.
- **Authentication on a WebSocket**: browsers cannot set an `Authorization` header on the handshake. Know the options (a short-lived ticket, a first-message token, a subprotocol) and their trade-offs.
- **Ordering and resumption**: sequence numbers, at-least-once delivery, idempotent clients.
- **Fan-out across replicas**: why in-process state breaks with two pods; Redis pub/sub (fire and forget) versus Redis Streams (persistent, replayable).
- **Backpressure**: what to do when the client reads more slowly than you produce.
- **Rate limiting**: fixed window, sliding window, token bucket; why it must be shared state.
- **Graceful shutdown**: what should happen to open sockets on `SIGTERM`.

## Build steps

### Protocol

- [ ] Write `docs/ws-protocol.md`: the envelope (`type`, `run_id`, `seq`, `payload`), every event type from the [brief](00-project-brief.md#websocket-protocol-sketch), error codes, and the reconnect handshake.
- [ ] Pydantic models for every event on the server. Generate the TypeScript types from the JSON schema so the two cannot drift.

### Server

- [ ] `WS /ws/conversations/{id}` with authentication and project membership check.
- [ ] Heartbeat: server pings, closes idle or dead connections.
- [ ] A **fake LLM streamer** behind an interface (`start run → async iterator of events`). Keep it permanently, switchable by configuration. E2E and load tests depend on it.
- [ ] Each run writes its events to a **Redis Stream** keyed by run ID. The WebSocket handler only reads from the stream and forwards. The producer and the socket are now decoupled.
- [ ] Resume: on reconnect the client sends `last_seq`; the server replays from the stream.
- [ ] Cancel: `run.cancel` sets a flag the producer checks between tokens.
- [ ] One active run per conversation, enforced with a Redis lock that has a TTL.
- [ ] Per-user rate limit using a token bucket in Redis; return a clear `error` event when limited.
- [ ] On completion, persist the user and assistant messages to Postgres in one transaction.
- [ ] On `SIGTERM`, stop accepting new runs, let in-flight runs finish or hand over, close sockets with a "going away" code.

### Frontend

- [ ] Vite + React + TypeScript, a router, login and register pages, token storage and refresh.
- [ ] Conversation list and history through TanStack Query.
- [ ] Chat view: token-by-token rendering, a stop button, connection status, automatic reconnect with exponential backoff and resume.
- [ ] Render markdown safely (sanitise; model output is untrusted input).
- [ ] Keep the socket logic in one hook or small client class that you can unit test without React.

### Two replicas

- [ ] In Compose, run two `api` replicas behind a reverse proxy (Caddy, Traefik or nginx) with WebSocket upgrade enabled and no sticky sessions.

### Tests

- [ ] Server: WebSocket protocol tests in pytest (happy path, bad token, cancel, resume from `last_seq`, rate limit).
- [ ] Frontend: Vitest tests for the socket client and the message reducer.
- [ ] First Playwright E2E: log in, send a message, see the streamed reply, reload and see history.
- [ ] Playwright reconnect test: go offline mid-stream, come back, assert the final text is complete with no duplicated tokens.
- [ ] First k6 WebSocket script: 50 concurrent conversations against the fake streamer; record time to first token and error rate as your baseline.

## Break it on purpose

- Kill one API replica mid-stream. The client should reconnect to the other replica and finish the message.
- Replace the Redis Stream with in-memory state for a moment and repeat. Watch it fail. This is the reason for the design.
- Throttle the browser network to slow 3G and stream a long answer. Check server memory.
- Open the same conversation in two tabs and send from both.
- Restart Redis during a run. Decide and document the intended behaviour.

## Definition of done

- [ ] A message streams correctly through either replica with no sticky sessions.
- [ ] Reconnect mid-stream produces a complete, non-duplicated message (covered by an automated test).
- [ ] Cancel stops token production within one second.
- [ ] The rate limit holds across both replicas.
- [ ] The k6 baseline numbers are written in `docs/journal.md`.

## Be able to explain

- Why would you choose SSE for an LLM chat, and what made WebSockets the better fit here?
- How do you authenticate a browser WebSocket, and what is wrong with a long-lived token in the query string?
- Why Redis Streams over pub/sub for this use case? What does pub/sub lose?
- What happens to an in-flight response when the pod serving it is terminated during a deploy?
- How does the client avoid showing a token twice after a reconnect?

## Resources

- [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)
- [Redis documentation](https://redis.io/docs/latest/) (Streams, pub/sub, Lua scripting)
- [Playwright documentation](https://playwright.dev/) (network emulation, WebSocket inspection)
- [Grafana k6 documentation](https://grafana.com/docs/k6/latest/) (WebSocket API)
