---
name: write-journal
description: >-
  Appends a work-session entry to docs/journal.md for Triage Copilot, covering
  what was built, what broke, and what was surprising. Use at the end of a
  session that changed the project, when the user asks to log or journal
  progress, or when updating the engineering log.
---

# Write a journal entry

`docs/journal.md` is the user's interview material. Keep entries short and concrete: commands, errors, measurements. No recap of the plan.

Write in first person, as the project author. Record only what happened. If something was not verified, write "not verified".

## Steps

1. Create `docs/journal.md` with the header below if it does not exist.
2. Use today's date as `## YYYY-MM-DD`. If that heading already exists, extend that entry instead of adding a second one.
3. Put the newest day first, directly under the header.
4. Name the phase when the session makes it clear. Otherwise leave it as `—`.
5. Leave a section out rather than filling it with "nothing".

## Header

```markdown
# Engineering journal

Newest entry first. One entry per work day.
```

## Entry

```markdown
## YYYY-MM-DD

**Phase:** 04
**Built:** Postgres checkpointer wired to the conversation id. Restarting the API no longer loses the thread.
**Broke:** First resume failed: the tool result had no matching tool call after trimming. Fixed by trimming whole pairs only.
**Surprised:** One checkpoint row per graph step, so a 6-tool run writes 6 rows.
**Next:** Stream tool events to the existing WebSocket protocol.
```
