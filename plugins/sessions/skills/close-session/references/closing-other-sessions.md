# Closing other sessions — frozen, crashed, or several at once

Read when this session closes sessions other than itself: a frozen tab, work
left by a crash or a reboot, or a batch before one follow-up session.

## 1. Sort the targets

Gather, in one pass:

- the working briefs still in `.claude/sessions/active/` (each live session
  has one; a brief without a matching handoff is a session never closed);
- which sessions your client still shows as open or running, if it can list
  them;
- the session transcripts (Claude Code keeps them as JSONL under
  `~/.claude/projects/<encoded-project-path>/`; `up-next`'s script lists the
  recent ones without a handoff).

Each target falls in exactly one class:

| Class | Sign | Closure |
|---|---|---|
| Warm | still open, recent activity | ask it to close itself (`/close-session`) |
| Cold | still open, idle for a long time | close it administratively, from here |
| Dead | brief or transcript left, no live process | close it administratively, from here |
| Excluded | the user keeps it running | leave it alone |

Do not wake a cold or dead session just to close it: resuming a long idle
context reloads it in full and costs far more than an administrative closure.

## 2. Freeze before changing shared files

If shared files (this skill, a shared config) must change first, ask the warm
sessions to "finish the current step without starting another, then wait",
and send them `/close-session` once the change is committed.

## 3. Order

1. A session whose uncommitted files another target also touches closes
   first, so its changes reach git before the next one inspects the diff.
2. Warm sessions get `/close-session`, all in the same turn when the client
   allows sending messages to other sessions; otherwise tell the user which
   tabs to close.
3. Cold and dead sessions are closed here, one after the other, each from its
   working brief, the last part of its transcript and the git state of its
   scope — never by reading its whole transcript.

## 4. Administrative closure of one cold or dead session

- Handoff: the usual template, `closed:` at the time of its last event, the
  closer named in Notes, even when the thread is `closed`.
- Work it left uncommitted: commit (if authorized) only what its brief or
  transcript shows as finished and tested, by explicit paths. Work cut by the
  crash stays uncommitted and is listed as "partial, not verified".
- Background jobs it launched: check whether they survived; record how to
  resume them, never relaunch them as part of the closure.
- Delete its working brief once the handoff holds its content.

## 5. Report

One final message for the batch, in the skeleton of `SKILL.md`, with one line
per target: slug · class · handoff link · commits or reservation. A target
that failed keeps its brief and makes the batch "closed with reservations".
