---
name: up-next
description: "Use only when the user explicitly asks which sessions to pick up or resume (\"/up-next\", \"what should I pick up?\", \"which sessions should I relaunch?\", « quelles sessions reprendre ? »). Sweeps recent handoffs and session transcripts, ranks open threads (firm deadlines and work at risk first, then declared priorities), lets the user pick in successive waves of questions until every candidate was seen, and launches the chosen ones as new sessions with ready briefs. Not for starting a single task (use start-session) or closing one (use close-session)."
---

# /up-next [days] [filter] — which sessions to pick up

Arguments: a number of days for the transcript sweep (default 7) and an
optional filter (a thread prefix or area). Threads come from handoffs whatever
their age; `days` bounds only the search for sessions that never closed.

Storage layout is defined once in
[references/storage.md](references/storage.md). In short: each closed session
leaves a handoff in `.claude/sessions/handoffs/` whose front matter carries
`thread`, `status`, `next`, `deadline`; the newest handoff of a thread is its
state. A thread id is `<area>-<subject>`: the area (first segment) is the
group used for questions and priorities. Live sessions keep a working brief in
`.claude/sessions/active/`.

## 1. Collect

1. **Run the bundled script** when Python is available (from the project root;
   pass this session's id if you know it so it is not listed as cut):

   ```bash
   python <this skill folder>/scripts/up_next.py scan --days 7 --exclude-session <id> --json <temp>/up-next.json
   ```

   It prints threads by status, sessions with no handoff (from Claude Code's
   JSONL transcripts in `~/.claude/projects/<encoded-project-path>/`), working
   briefs left in `.claude/sessions/active/`, and threads declined in earlier
   passes. Read the printed summary, not the JSON, unless you need a field.
   `--no-transcripts` reads handoffs only; `--all` adds paused threads.
2. **Without the script**: list `.claude/sessions/handoffs/`, read only the
   front matter of each file, keep the newest per `thread`, and list
   `.claude/sessions/active/`. No transcripts in this mode: say so in the report.
3. **Handoffs without front matter, and cut sessions** (no handoff, or
   `close-session started` without one) need a thread and a status. Classify
   them yourself up to about 40 items; beyond, one subagent per batch, batches
   never sharing an item, with
   [references/classify-mandate.md](references/classify-mandate.md). A cut
   session whose work is lost or half-written is a candidate for a closure from
   here (see `close-session`), not only for a relaunch.
4. **What holds a thread**: sessions still running (the client's session list
   if it has one; `maybe still running` in the script output; a recent working
   brief naming the thread). A held thread is never offered.
5. If the run log has frictions from the last pass (`.claude/sessions/up-next-log.jsonl`),
   keep them in mind.

No handoffs and no transcripts: say so and stop. Suggest `close-session` at the
end of the next sessions so threads accumulate.

## 2. Rank — urgency first, then declared priority

A thread is **urgent** when one of these holds, each with its source:

- a **firm** deadline within 14 days or already past. A **marker** date is
  never urgent and never "late", even once past: write "marker of <date>";
- **work at risk**: uncommitted files, a worktree about to vanish, a download
  or computation stopped midway. Check the live state (git, processes) and
  write "proven" or "estimated";
- a result to verify before anything is sent or published;
- a user decision (`waiting`) that blocks other work.

After urgency, order by the declared priorities in
`.claude/knowledge/priorities.md` (a ranked list of areas, matched on the
first segment of the thread id). Missing or older than 30 days: ask about it
in wave 0, and on first use offer to create it. Unranked areas follow by their
newest handoff; paused ones come last and rise only on real loss or an external
deadline. Threads declined in two earlier passes go to the end.

Split each thread as **session** (an agent can do it), **user only** (create an
account, post, apply, buy, approve) or both. `blocked` threads go to the
report, never to a question.

Optional **route**: when a thread's next action clearly needs a stronger model
or higher effort (hard bug, architecture, in-depth study, security review) or
can run on a cheaper one (routine edits), state it in the option. Ticking the
option approves that route for that session.

## 3. Decide — waves until every candidate was seen

**Filter first.** Put "out of waves", with the reason, every thread whose next
action cannot start now: it opens on a later date, states an unmet
precondition ("once X is merged"), reads a file that does not exist, or is the
user's own act (that one goes to "Waiting on you"). Check "already done?":
a newer commit, handoff or deliverable that does the next action; drop it from
the waves and name the evidence. Threads that a recent handoff cites together
become one option ("merged with …").

**Wave 0 — scope**, real choices only (a choice with an obvious answer is
written "Decided: …" in the report instead):

- how many sessions to launch this pass (recommend fewer when the user's plan
  limits are nearly used, if you can read them);
- which areas or projects first (multi-select), each with its counts
  ("api — 1 urgent, 4 ready"); a filter argument replaces this question;
- the declared priorities, if missing or stale.

**Selection waves**, as many as the queue needs:

- Three thread questions, then one "Continue?" question. When four questions
  or fewer remain, the wave is the last: up to four thread questions.
- Thread question: one group (area or project), multi-select, three threads
  plus "None", recommended first, header `<group> <i>/<n>`, the question naming
  the room left ("api — which ones? (3 left)"). Option label: the thread in
  five words. Description, readable alone: next action, why now (deadline,
  risk, rank), date of the newest handoff, route if any, and flags such as
  "small: done here" or "merged with X".
- Give each chosen priority at least two waves when it has the threads for it;
  widen with its `waiting` threads a session can prepare, never by showing a
  done or held thread.
- Just before each wave, re-check its threads silently (newer handoff, commit,
  deliverable, a session now holding it). Never show work already done.
- "Continue?": continue with the next groups (recommended while room is left);
  skip the current group; launch the ticked ones now; stop and launch nothing.
- Never show a thread twice in a pass. Ticks beyond the room chosen in wave 0
  go to the report as "postponed, cap".
- Keep text between waves to a minimum: some clients hide it while a question
  is open.

**Closing questions**, in the last wave if it has room: which user-only
actions to prepare (draft, checklist); which threads declined again after two
earlier passes to pause.

**No question tool?** Put the whole queue in one message instead: numbered
threads grouped by area, each with its one-line description and a recommended
set; the user answers with numbers.

## 4. Launch

- **Small next action: do it here.** A next action that fits in a few calls
  (one file, one setting, one command, one short text) is done by this session
  after the launches; a new session reloads the whole project context and costs
  more than the work. Its option says "small: done here".
- **Merge only on shared scope**: ticked threads that touch the same files or
  where one needs the other's result go to one session, in order. Same project
  alone is not a reason. Its brief lists every thread id.
- **One brief per launched session**, in
  [references/session-brief.md](references/session-brief.md): goal, done
  when, read first, limits, deliverable, closing. Pointers, not copied state.
- **Uncommitted work** resumes in the same checkout, never in a fresh
  worktree (a new worktree starts from the last commit and does not see it).
  Threads whose scopes may overlap run in separate worktrees when the client
  offers them.
- **Starting the session** is client-specific. If the client offers a tool to
  open a new session or task with a prompt, use it with the brief, apply the
  route (model, effort) when the tool allows it, and read back what was
  applied; never claim a route that was not applied. Otherwise, give each brief
  as a ready-to-paste block under a bold title, with the route on the line
  above it: "open a new session with this brief".
- A thread whose session is still open gets a short message to that session,
  not a new brief.
- A tooling defect found while sweeping becomes a proposal in the report, not a
  fix in this pass.

## 5. Report

One line per launched session (link or title), the user-only actions left with
their dates, the threads out of waves with their reasons, the threads closed,
paused or classified by this pass, the waves asked and threads seen against the
queue ("5 waves, 27 threads seen of 30"), the "Decided" choices of wave 0, and
the proof gaps (estimated, unread source, no transcripts). Never predict the
results of launched sessions.

Pausing a thread writes a new short handoff for it with `status: paused` and the
reason; handoffs are never edited.

## 6. Retex — every pass

Log the pass (the script's `log` command, or one JSON line appended by hand):

```bash
python <this skill folder>/scripts/up_next.py log --shown a,b,c --launched a --declined b,c --note "what was slow, wrong or asked twice"
```

Threads declined in two passes are then shown last. When a friction repeats
or costs real time, propose a precise change to this skill at the end of the
pass; never edit the skill silently.
