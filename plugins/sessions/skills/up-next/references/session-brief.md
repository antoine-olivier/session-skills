# Brief for a launched session

One brief per launched session or merged group. One line per field, in the
user's language, under about 1,500 characters. Pointers rather than copied
state: the new session reads the sources itself.

```text
Goal: <what to achieve, and why it matters now>
Done when: <observable check: test passes, file exists, figure read, PR open>
Read first: <thread id> · <its newest handoff path> · <files or commits it names>
            · <sibling sessions sharing the scope, if any>
Limits: <paths it may write> · no push, deploy, publish, send, buy or delete
        without the user's consent · <checkout: same checkout (uncommitted work)
        or own worktree>
Deliverable: <what the user gets: commit, file, draft, decision to make>
Closing: run close-session; its handoff carries thread `<thread id>`
         (merged group: every thread id) so /up-next sees the update.
```

Put the route, when there is one, outside the brief: in the launch tool's
model and effort fields, or on the line above a pasted block
("Route: stronger model, high effort — hard bug").

When the client cannot open sessions itself, present each brief as:

**<Thread title>** — Route: <route or "default">

    <the brief>

and say: "open a new session with this brief".
