# session-skills

Claude Code skills to start, close and resume sessions without losing context. I use them every day; they are cleaned up to work on any machine.

## Install

In Claude Code:

```
/plugin marketplace add antoine-olivier/session-skills
/plugin install sessions@session-skills
```

Skills then load on their own when the task matches. Each one is a plain
`SKILL.md`, so other agents that read that format can use them too: copy the
folder from `plugins/sessions/skills/`.

All my skill packs are also listed in one catalog:
[antoine-olivier/agent-skills](https://github.com/antoine-olivier/agent-skills).

## Skills

- **start-session**: starts or resumes work from the last handoff.
- **close-session**: saves only durable knowledge and real commitments, then writes a handoff.
- **up-next**: sweeps recent sessions and ranks the open threads worth resuming.

## License

MIT. Some parts are adapted from other MIT-licensed skills: see
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
