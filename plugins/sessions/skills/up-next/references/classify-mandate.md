# Mandate — classify handoffs and cut sessions into threads

For handoffs without front matter and sessions that ended without a handoff.
Fill the placeholders and pass the text as the subagent prompt. One subagent
per batch; batches never share an item.

```text
Read-only, except <output path>. No other file, no commit.

Input: <list of items>. Each item is either a handoff path under
.claude/sessions/handoffs/, or a session line from up_next.py (session id,
title, dates, last user and assistant messages, transcript file name under
<transcript folder>). Open a transcript only when the line is ambiguous, and
read only its last ~50 records.

Known threads (id — next): <list from the scan>.

Goal: assign EVERY item to exactly one thread. A thread is one line of work
followed over one or more sessions: same deliverable, operation or question.
Reuse a known thread when the item continues it. Do not merge two different
deliverables into one thread.

Write one JSON object per thread, one per line (JSONL), to <output path>:
{"thread": "<lowercase-kebab id>", "status": "open|waiting|blocked|paused|closed",
 "next": "<one concrete action, <= 30 words; empty when closed>",
 "deadline": "<YYYY-MM-DD firm|marker, or empty>",
 "items": ["<every item of the thread>"],
 "evidence": "<one line: why this status>"}

Status, judged on the newest item and anything later:
- closed: a later item did the next action, or nothing committed remains;
- open: an explicit next action an agent session can do, not done later;
- waiting: the next step needs the user (decision, approval, command, purchase);
- blocked: waits on a third party;
- paused: kept for later with no stake now. An open or blocked thread whose
  newest item is older than <stale date> becomes paused unless it has a
  deadline ahead or work is at risk. A waiting thread never becomes paused.
A cut session whose last messages show work in progress is open, with
"resume and close: <what was in progress>" as its next action.

Final message, <= 30 lines: counts per status, every live thread as
"id — next", and doubts. Nothing else.
```

After the batches return, the main session writes one short handoff per
classified thread that has none (front matter only, plus a title and the
evidence line; `session:` set to the cut session's id when there is one), so
the next pass does not classify the same items again.
