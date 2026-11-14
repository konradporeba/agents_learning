---
name: write-adr
description: >-
  Writes an architecture decision record under docs/adr for Triage Copilot.
  Use when a real technical decision is made or reversed — a library, data
  store, model, queue, agent structure, or deployment approach with
  alternatives and consequences — or when the user mentions an ADR or a
  decision record.
---

# Write an ADR

One decision per file. Record a decision the user actually made. If they are still choosing, status is `proposed` and the decision section states the open question.

Skip an ADR for naming, formatting, or a choice with no realistic alternative.

## Steps

1. Read `docs/adr/` (create it if missing). Next number is one above the highest `NNNN` prefix, starting at `0001`.
2. Write `docs/adr/NNNN-kebab-title.md` using the template.
3. If this replaces an earlier ADR, set that file's status to `superseded by NNNN` and name it here.
4. Use today's date. Do not invent options the user did not consider; ask if the alternatives are unknown.

## Template

```markdown
# NNNN. Short title in the imperative

- Status: proposed | accepted | superseded by NNNN
- Date: YYYY-MM-DD

## Context

What forced the decision, in a few sentences. Constraints and requirements only.

## Decision

What was chosen.

## Alternatives

- **Option.** Why it lost. One or two sentences each.

## Consequences

What becomes easier, what becomes harder, and what we must revisit later.
```

## Example

A choice of Postgres for LangGraph checkpoints, with Redis and MongoDB rejected because LangGraph ships a Postgres checkpointer and the checkpoint must be transactional with the message write:

```markdown
# 0004. Store LangGraph checkpoints in Postgres

- Status: accepted
- Date: 2026-11-14

## Context

Agent state has to survive a process restart, and the message transcript is already in Postgres.

## Decision

Use the LangGraph Postgres checkpointer. `thread_id` is the conversation id.

## Alternatives

- **In-memory checkpointer.** Lost on restart, so it fails the phase outcome.
- **Redis.** Fast, but it is not a supported LangGraph checkpointer and the state would not commit with the transcript.

## Consequences

Checkpoint tables appear in the same database as app data. A checkpoint schema change is now a compatibility concern during deploys.
```
