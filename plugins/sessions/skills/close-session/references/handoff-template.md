# Handoff template

Path: `.claude/sessions/handoffs/YYYY-MM-DD-HHMM-<slug>.md` (see
`storage.md`). Sections marked "only if any" are omitted when empty.

```markdown
---
thread: <thread id>
status: open | waiting | blocked | paused | closed
next: <the one next action; empty when closed>
deadline: <YYYY-MM-DD firm|marker — only if any>
session: <client session id, if known>
closed: YYYY-MM-DD HH:MM
---

# <Title: result or subject>

Scope: <paths this session wrote>

## Result (verified)

- <fact, with its evidence: command run, file:line, figure read>

## Prepared or unverified

- <started, drafted or untested work, and its exact state> — only if any

## Decisions

- <decision, who made it, when> — only if any

## Files

- <files changed, commits; uncommitted files listed as such> — only if any

## Waiting on you

- <decision, approval or command only the user can give> — only if any

## Next action

<The same action as `next`, detailed: what to read first, what "done" means,
anything that conditions it.>

    <ready-to-paste prompt to resume, only if useful>

## Suggested skills

- <skill the next session should load, and why> — only if any

## Notes

- <observation with no commitment, known limit, proposed check> — only if any
```

Rules:

- `closed` holds exactly `YYYY-MM-DD HH:MM`. For a frozen session closed by
  another one, use the time of its last event, and name the closer in Notes.
- Never add a "leftovers" or "maybe later" section: anything listed there
  reads as an open follow-up to the next pass. A loose idea goes to Notes.
- A status other than `closed` needs a non-empty `next`.
