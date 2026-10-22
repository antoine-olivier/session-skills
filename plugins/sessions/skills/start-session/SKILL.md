---
name: start-session
description: "Use at the start of multi-step work, when the user names a project to work on (\"/start-session <project> [theme]\", \"let's work on <project>\", « on bosse sur <project> »), resumes a previous session, or opens with no task (\"hi\", \"what's next?\"). Sets scope and autonomy before the first write, creates a working brief that survives compaction, loads only the project knowledge the task needs, and offers the project's open threads. Not for one-off questions or single-step edits."
---

# Start session

Start the requested work. Opening is not a separate interview: do not load
every note, the whole history or unrelated open items.

Storage layout is defined once in
[references/storage.md](references/storage.md). In short: working briefs in
`.claude/sessions/active/`, handoffs (with each thread's state in their front
matter) in `.claude/sessions/handoffs/`, durable facts in `.claude/knowledge/`.
Create a folder only when you first write to it.

## 1. Scope and autonomy — before the first write

- **Scope**: the precise paths this session will write. Keep it narrow; widen
  it explicitly when the task grows.
- **Autonomy level**, one of:
  - *semi-automatic* — confirm before the first edit in each folder;
  - *automatic* (default) — local edits and reversible checks are free;
  - *autonomous* — unattended run; open choices become `waiting` threads
    instead of questions.
  In every level, pushing, deploying, publishing, sending, buying and
  deleting need the user's explicit consent for that action.
- Announce the default in one line ("Decided: automatic") instead of asking.
  Ask only when semi-automatic or autonomous is genuinely in play, or the user
  asks; never when the prompt already fixed it.
- If the client has permission modes, align them with the level (stricter
  mode for semi-automatic). Never bypass permissions to go faster.
- Check `git status` before the first write in each repository. Uncommitted
  changes you did not make belong to someone else: do not commit, restore,
  stash or overwrite them. If another live session owns the same paths (its
  brief in `.claude/sessions/active/` names them), resolve the overlap with the
  user before writing.

## 2. Working brief

For multi-step work, create `.claude/sessions/active/<slug>.md` with the first
write (template in `references/storage.md`). It is what survives a context
compaction: a summary loses decisions, corrections and identifiers first, the
brief keeps them.

- Update it in the same turn as each decision, authorization, user correction
  or milestone. Replace stale lines; never append a log.
- After a compaction, re-read it before acting.
- Paths, decisions and identifiers only: no secrets, no copied file contents.
- Keep it out of git (it is scratch); `close-session` turns it into the
  handoff and deletes it.

## 3. Relevant context — bounded

Before a project decision or its first change:

- Read the project's entry points (README, `CLAUDE.md` or equivalent) and
  only the `.claude/knowledge/` files whose topic the task touches. Read
  `lessons.md` headings and the lines under the relevant theme.
- Read a handoff only when resuming its thread: the newest handoff of that
  thread, not the whole folder.
- For "does X exist?", the disk and git are the truth; a note says what was
  true when it was written.
- A historical note is evidence, not a newer instruction. The user's current
  request overrides older notes.

## 4. Argument: a project or theme

When the user names a project (`/start-session <project> [theme]`, "let's work
on <project>"):

1. No project named: ask which one, offering the projects of the most recent
   handoffs.
2. Open it as in § 3, plus its git state.
3. List the project's open threads: the newest handoff per `thread` in
   `.claude/sessions/handoffs/` with `status: open` or `waiting` (front matter
   only; `up-next`'s script does this if available). Offer them as one choice:
   each thread with its `next` action, the recommended one first, plus "None".
   No handoffs yet: say so in one line and go on.
4. Then ask up to three or four questions on the project's real forks for this
   session, recommended option first, each option tied to a fact you read. Not
   a closed plan to approve.
5. Extra words after the project name (`<project> seo`) narrow the session to
   that theme.

Without a project argument, opening stays free of questions.

## 5. First message is not a task

When the user opens with "hi" or "what's next?":

- Lead with what is waiting on them: `waiting` threads and firm deadlines from
  the newest handoffs, one line each.
- Propose at most three session ideas, from open threads, as one choice. The
  chosen one starts right away in this session, or as a new session with a
  brief if the client can open one (see `up-next` for the brief format).
- For a full sweep of open threads, suggest `/up-next`.

## 6. Talking to the user

- State the useful next action and any real conflict in a short update. No
  ceremonial opening report.
- Ask only genuinely open choices. When one option clearly wins, write
  "Decided: X" in one line and proceed. Routine reversible details are decided
  from the request.
- If the client has a multiple-choice question tool, use it, up to four
  questions per round, recommended option first. Otherwise put all needed
  questions in one message: numbered questions, lettered choices, one
  recommendation each.
- Before announcing a duration, separate machine time from the user's turns;
  agents tend to overestimate badly, so prefer a range and say it is an
  estimate.
- Keep the configured model; do not switch it silently.
- If the client can set a tab or session title, set it once the subject is
  known and rename it only when the subject changes.

## Done when

Requested work has started with the right scope and autonomy level, the brief
exists for multi-step work, the relevant sources were found, and no needless
question or memory dump was introduced.
