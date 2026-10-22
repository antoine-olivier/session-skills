# Session storage convention

The three skills of the `sessions` plugin (`start-session`, `close-session`,
`up-next`) share one small, project-local layout. Each skill creates what it
needs on first use; nothing else is required. The same file ships in each
skill folder so that any one of them works alone.

```text
<project root>/.claude/
  sessions/
    active/<session-slug>.md      working brief of a live session (scratch)
    handoffs/YYYY-MM-DD-HHMM-<slug>.md   one per closed session
    up-next-log.jsonl             optional: one line per /up-next pass
  knowledge/
    <topic>.md                    durable facts, decisions and constraints
    lessons.md                    errors not to repeat, methods that worked
    priorities.md                 optional: declared project order, dated
```

The project root is the folder the session works in (usually the git root).
Use forward slashes in links. Never store secrets, credentials or personal
data the user did not ask to keep in any of these files.

## Version control

Commit `handoffs/` and `knowledge/` when the project is shared and they hold
nothing private: they are project memory. Keep `active/` and
`up-next-log.jsonl` out of git (add `.claude/sessions/active/` and
`.claude/sessions/up-next-log.jsonl` to `.gitignore` the first time a skill
creates them, if the project uses git and the user agrees).

## Working brief — `sessions/active/<session-slug>.md`

Created by `start-session` for multi-step work, kept current during the
session, turned into the handoff by `close-session`, then deleted. It is what
survives a context compaction or a crash: after a compaction, re-read it
before acting. At most about 60 lines; replace stale lines, never append a log.

```markdown
# <slug> — <one-line intent>

session: <client session id, if known>
started: YYYY-MM-DD HH:MM
thread: <thread id this session continues or opens>
scope: <paths this session may write>

## Done and verified
## Decisions and authorizations   (each with when and who decided)
## User corrections
## Identifiers, figures, paths
## Files in progress
## Rejected approaches            (and why)
## Next step
```

## Handoff — `sessions/handoffs/YYYY-MM-DD-HHMM-<slug>.md`

Written by `close-session` (and by `up-next` when it pauses a thread or
records a classified one). A handoff is never edited after the fact: a later
session writes a new one for the same thread. The front matter is the
machine-readable part; `up-next` reads only it plus the title.

```markdown
---
thread: <area>-<subject>, lowercase kebab, e.g. billing-csv-export
status: open | waiting | blocked | paused | closed
next: <one concrete action, at most ~30 words; empty when closed>
deadline: <YYYY-MM-DD firm | YYYY-MM-DD marker; omit when none>
session: <client session id, if known>
closed: YYYY-MM-DD HH:MM
---

# <Title: result or subject>
```

Body sections: the `close-session` skill's `references/handoff-template.md`.

**Threads.** A thread is one line of work followed over one or more sessions:
same deliverable, operation or question. Its state is the front matter of its
newest handoff. Its id is `<area>-<subject>` in lowercase kebab case
(`api-csv-export`, `docs-install-guide`): the first segment is the **area**
(a component, sub-project or theme of this project) that `up-next` groups
questions by and that `priorities.md` ranks. Reuse existing areas before
inventing one; a small project may use a single area. Statuses:

- `open` — a session can do the next action now;
- `waiting` — the user must act (a decision, an approval, a command on their
  machine, sending, buying); `next` names that act;
- `blocked` — a third party must act (reply, access, payment);
- `paused` — kept, no stake now;
- `closed` — nothing remains.

At most one next action per thread. Split a second independent action into
its own thread.

**Deadlines.** `firm` is an external dated constraint (a filing, an event) or
a milestone set for the project (an announced release). `marker` is a date
set only so as not to forget: it is never "late". An untyped date is a marker.

## Durable knowledge — `knowledge/`

One file per topic (`knowledge/<topic>.md`, e.g. `deploy.md`, `api.md`); look
for an existing topic before creating one. One entry per fact:

```markdown
## YYYY-MM-DD — <fact or decision, one line>

<Precise statement, scope, condition of validity.>
Source: <path:line | URL | commit | "user, in session">. Status: decided | observed | inferred.
```

A preference or decision is `decided` only if the user expressed it; one the
agent inferred is `inferred`, with what supports it. A newer entry that
supersedes an older one says so and keeps the old one; never silently rewrite
or delete a dated fact.

`lessons.md` holds one line per lesson, grouped under `## <theme>` headings:

```markdown
- Don't: <rule> — <why> (source: <path:line or commit>, YYYY-MM-DD)
- Do: <rule> — <why> (source: …, YYYY-MM-DD)
```

`priorities.md` (optional, written only when the user states an order):

```markdown
# Priorities — decided YYYY-MM-DD
1. <area>
2. <area>
Paused: <area>, …
```

## What never goes there

- Routine progress, file lists, test output: the handoff, or nowhere.
- What is re-read at its source anyway: documentation, git state, file content.
- Unverified negative claims ("X does not work").
- Facts appended to `CLAUDE.md`, `AGENTS.md` or another always-loaded
  instruction file, unless the user explicitly asks: those stay short. A
  single pointer line ("durable project facts: `.claude/knowledge/`") is the
  most such a file needs, and only with the user's agreement.
