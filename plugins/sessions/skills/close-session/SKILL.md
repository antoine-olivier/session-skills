---
name: close-session
description: "Use when the user explicitly stops, asks to close, wrap up or hand off a session (\"close the session\", \"let's stop here\", \"handoff\", « on clôture », « on s'arrête là »), or asks to close a frozen or crashed session. Writes a handoff the next session can resume from, saves only genuinely new durable knowledge and the commitments that were really made, and updates the thread for /up-next. Not for a mid-session recap or progress summary, and not when the user only pauses for a moment."
---

# Close session

Write a handoff the next session can act on, and keep only what is durable.
Work from the current context; do not re-read the whole transcript.

Storage layout (handoffs, threads, knowledge files) is defined once in
[references/storage.md](references/storage.md). In short: the handoff goes to
`.claude/sessions/handoffs/YYYY-MM-DD-HHMM-<slug>.md` with a front matter of
`thread`, `status`, `next`, `deadline`, `session`, `closed`; durable facts go to
`.claude/knowledge/`. Create the folders if they are missing.

## 0. Is closing the right move?

At the end of a phase (never mid-phase), test in order; the first "yes" wins:

1. **Continue** — the next phase needs this context as its primary source.
2. **Clear** — everything in this context is now disposable: `/clear`, no handoff.
3. **Handoff** — something has to travel: a new session, another directory,
   a colleague, a side task split off. Run this skill.
4. **Subagent** — a bounded task that can run without the user: delegate it.
5. **Compact** — last resort, and only with the user's agreement.

An explicit request from the user to close beats the tree: run this skill.

## 1. Settle running work

- Stop or wait for any background task still running, and note how to resume it.
- Move any durable artifact that exists only in a scratch or temp folder into
  the project (temp folders can vanish with the session), or name it in the
  handoff as lost on close.
- Start from the working brief `.claude/sessions/active/<slug>.md` if it
  exists: it carries decisions, authorizations and rejected paths from before
  any compaction. Check it against the transcript and `git status`; they win
  on conflict.

## 2. Pick the thread

Every closure belongs to exactly one thread (definition and statuses in
`references/storage.md`).

- Reuse the thread this session continued: the one named in the brief, in the
  opening prompt, or in the handoff it resumed. To list existing threads, read
  the front matter of the newest handoffs (`.claude/sessions/handoffs/`).
- Otherwise create an id `<area>-<subject>` (`billing-csv-export`), reusing an
  area already used by other threads when one fits.
- Pick its status — `open`, `waiting`, `blocked`, `paused` or `closed` — and
  **at most one** next action. A second independent follow-up becomes its own
  thread with its own handoff, or goes to Notes if nobody committed to it.
- A deadline is `firm` only if it is an external constraint or a project
  milestone; otherwise `marker`.
- Optional: when the next action clearly needs a stronger or cheaper model or
  a specific effort level, say so in one line under "Next action".

## 3. Write the handoff

Use [references/handoff-template.md](references/handoff-template.md). Rules:

- Separate what is **done and verified** from what is prepared, started or
  unverified. A claim without evidence says "not verified".
- Point to existing artifacts (file, commit, URL) by path instead of copying
  their content.
- Record every decision and authorization with who gave it and when.
- **Commitments only if real**: an item enters "Waiting on you" or becomes the
  next action only if the user or the session explicitly committed to it. A
  loose idea goes to Notes, never as a follow-up. A closure with no follow-up is
  normal: status `closed`, empty `next`.
- When the next action needs a skill, list it under "Suggested skills".
- The front matter `session:` field holds the client's session id when known:
  `/up-next` uses it to tell closed sessions from cut ones.

## 4. Save durable knowledge — sparingly

Default: nothing new. Session status belongs in the handoff, not in memory.

A **fact or decision** goes to `.claude/knowledge/<topic>.md` (format in
`references/storage.md`) only if all hold:

- it changes future work on this project;
- it is not already available from its source (code, docs, git history);
- it is stated by the user, or verified, with a source; an inferred
  preference is marked `inferred` or not stored.

A **lesson** (an error not to repeat, a method that proved itself) goes to
`.claude/knowledge/lessons.md` as one line, only if all four hold:

1. it recurs (seen twice, or once at a costly or irreversible stake);
2. it is codifiable: applicable without this session's context;
3. it changes what the next session does;
4. it stays right when read cold, away from the incident that produced it.

Look first: sharpen an existing line rather than add a near-duplicate. A
closure with zero new lessons is normal. Details:
[references/promotion-rules.md](references/promotion-rules.md).

**Mechanical or judgement?** A mechanical slip a script would have caught
becomes a proposed check or hook in the handoff Notes, built only after the
user agrees. A judgement error becomes a lesson (criteria above).

A reusable tool or script created during the session gets one line in the
relevant knowledge file: path, how to run it, what it reads and writes.

Never append facts to `CLAUDE.md`, `AGENTS.md` or another always-loaded
instruction file unless the user asks.

## 5. Commit and clean up

- If the user authorized committing, commit only this session's own files, by
  explicit path, after reading the staged diff. Never `git add -A`, never
  sweep in another session's changes, never amend or force anything. Without
  that authorization, list the uncommitted files in the handoff.
- Delete this session's working brief once the handoff holds its content.
- Group the final checks into one command where possible (handoff exists,
  front matter parses, commit landed).

Optional: on a large closure, delegate the mechanical part (commit, link
checks) to a subagent with exact paths and file ownership, then review its
evidence. Do not create a new session for it.

If closure leaves a choice only the user can make, ask it in one compact round
(with the client's multiple-choice question tool if it has one). In an
unattended run, do not ask: record the thread as `waiting` with that choice as
its next action.

Closing a session other than this one (frozen tab, crash, several at once):
[references/closing-other-sessions.md](references/closing-other-sessions.md).

## 6. Final message

The user reads it to decide one thing: can they close the tab. Put the marker
on both the first and the last line (clients often scroll to the bottom), 3 to
6 lines between, one bullet per visible line, in the user's language:

```markdown
# Session closed
Everything is written and committed — you can close this tab.

---
- Done: <the verified result, one sentence>
- Waiting on you: <decision, approval or command> — only if any
- Verified: <the key evidence, a figure that was read> — only if any
- Trace: <handoff link> · thread `<id>` (<status>) · <only the layers written>
- Next time: <the thread's next action> — only if any

# Session closed
```

- "Waiting on you" gathers every act only the user can do, one line each.
- "Trace" shows only what changed: the handoff link and thread are always
  there; a knowledge entry, a lesson or a commit appears only if written. No
  "nothing changed" lines.
- Commit hashes, test breakdowns and file lists live in the handoff, not here.
- If any required step failed (commit, write, check), the second line becomes
  `Closure incomplete — <what blocks, one line>.` and both headings become
  `# Session closed with reservations`. Never print the success line over a
  failed step.
- If the client can rename the tab or send a notification, doing so is a
  courtesy; its failure is one extra line, never a reason to withhold closure.
