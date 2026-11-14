# 0001. Use project rules and skills for the engineering log

- Status: accepted
- Date: 2026-11-14

## Context

The learning plan's working rules have to apply to every Cursor model used on this repo. Decisions and session notes need a fixed place and format, or the interview log will not get written.

## Decision

Put the six working rules in `.cursor/rules/` as always-apply project rules. Add two project skills, `write-adr` and `write-journal`, for `docs/adr/` and `docs/journal.md`.

## Alternatives

- **User rules in Cursor settings.** They would apply to every project, not only this one.
- **A separate custom agent.** The journaling and ADR tasks are workflows for the agent already working in the repo. A second agent adds setup without changing the format.

## Consequences

The rules and skills travel with the repo once committed, and they do not affect other projects. An explicit "write this for me" or "don't log this" in the current message still overrides them. The rules only help if a chat actually loads them; that was not verified from this session.
