# What becomes durable knowledge

A fact is stored only when it changes future work and is not already
available from its current source. Routine progress, file lists and
incomplete work belong in the handoff, not in permanent memory.

| Kind | Destination |
|---|---|
| Project constraint or decision | `.claude/knowledge/<topic>.md`, dated, with source and status |
| Lesson (error not to repeat, method that worked) | `.claude/knowledge/lessons.md`, one line, four criteria in `SKILL.md` |
| Declared project order | `.claude/knowledge/priorities.md`, only when the user states it |
| Session state, next steps, open questions | the handoff |
| A real milestone | the handoff, and the project's changelog or history if it keeps one |

## Admission

- A preference or decision is recorded as such only if the user expressed it.
  One the agent inferred is marked `inferred` with what supports it, or not
  stored.
- Do not capture what is re-read at its source anyway: a tool's documentation,
  git state, file content.
- Do not store unverified negative claims about a tool ("X doesn't work").
- Do not store transient operational facts (a server that was down, a quota
  that was hit today).
- Current permissions and authorizations live with the session that holds
  them, not in a note the next session may never read.

## Conflicts and history

- Preserve old entries and date the superseding statement ("Supersedes the
  entry of YYYY-MM-DD"). Do not merge, delete or silently rewrite an old fact.
- On a real conflict between two sources, keep both and ask the user to
  decide only what is actually unclear.

## Always-loaded instruction files

`CLAUDE.md`, `AGENTS.md` and similar files are loaded into every session and
must stay short. Never move facts into them to "make sure they are seen".
With the user's agreement, one pointer line to `.claude/knowledge/` is enough.

## Reorganizing knowledge

Only when the user asks, or a link in a knowledge file is broken — never as a
routine part of a closure:

1. Reproduce the problem (a fact that cannot be found, a dead link).
2. Note the size and content of each file you will change; a reorganization
   must not erase a fact that exists in only one place.
3. Repair the specific link or entry. Merging or deleting entries needs the
   user's explicit agreement for the named files.
4. Check every link you touched and look the fact up again the way a future
   session would. A failed search is not proof that a fact does not exist.
