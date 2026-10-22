#!/usr/bin/env python3
"""List open threads and unclosed sessions of a project, for /up-next.

Reads two sources, both optional:

1. Handoffs in <project>/.claude/sessions/handoffs/*.md. Each starts with a
   front matter (thread, status, next, deadline, session, closed); the newest
   handoff of a thread gives its state.
2. Claude Code transcripts (JSONL) in <config>/projects/<encoded-project>/,
   where <config> is $CLAUDE_CONFIG_DIR or ~/.claude and the encoded name is
   the absolute project path with every non-alphanumeric character replaced
   by "-" (for example /home/user/myproject -> -home-user-myproject). A
   recent session that no handoff names, and that wrote no handoff, is listed
   as a cut session.

It also lists working briefs left in .claude/sessions/active/ and, with
`log`, records one line per /up-next pass so threads declined twice can be
shown last.

    python up_next.py scan [--project DIR] [--days 7] [--projects-dir DIR]
                           [--exclude-session ID] [--all] [--no-transcripts]
                           [--json FILE]
    python up_next.py log [--project DIR] [--shown a,b] [--launched a]
                          [--declined b] [--note "what got in the way"]

The script only collects and pre-sorts; the agent ranks and decides.
Standard library only, read-only except for `log`.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HANDOFFS = Path(".claude") / "sessions" / "handoffs"
ACTIVE = Path(".claude") / "sessions" / "active"
LOG = Path(".claude") / "sessions" / "up-next-log.jsonl"
STATUSES = ("open", "waiting", "blocked", "paused", "closed")
URGENT_DAYS = 14          # a firm deadline within this many days is urgent
LIVE_MINUTES = 15         # a transcript touched this recently may still be running
EXCERPT = 200             # characters kept from a message
WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
REMINDER = re.compile(r"<system-reminder>.*?</system-reminder>", re.DOTALL)
COMMAND = re.compile(r"<command-name>\s*([^<\s]+)\s*</command-name>")


# ---------------------------------------------------------------- handoffs

def read_front_matter(path: Path) -> tuple[dict, str]:
    """Return (fields, title) of a handoff; fields empty when there is none."""
    try:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return {}, ""
    lines = text.splitlines()
    fields: dict[str, str] = {}
    body_start = 0
    if lines and lines[0].strip() == "---":
        for i, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                body_start = i + 1
                break
            key, sep, value = line.partition(":")
            if sep:
                fields[key.strip().lower()] = value.strip()
    title = next((l[2:].strip() for l in lines[body_start:] if l.startswith("# ")), "")
    return fields, title


def parse_deadline(raw: str) -> dict | None:
    match = re.search(r"(\d{4})-(\d{2})-(\d{2})", raw or "")
    if not match:
        return None
    try:
        day = date(*map(int, match.groups()))
    except ValueError:
        return None
    kind = "firm" if re.search(r"\bfirm\b", raw, re.IGNORECASE) else "marker"
    return {"date": day.isoformat(), "kind": kind, "days_left": (day - date.today()).days}


def collect_threads(root: Path) -> tuple[dict, set, int]:
    """Newest handoff per thread, the session ids handoffs name, handoff count."""
    folder = root / HANDOFFS
    threads: dict[str, dict] = {}
    sessions: set[str] = set()
    per_thread: dict[str, int] = {}
    count = 0
    if not folder.is_dir():
        return threads, sessions, count
    for path in sorted(folder.glob("*.md")):
        fields, title = read_front_matter(path)
        count += 1
        if fields.get("session"):
            sessions.add(fields["session"])
        thread = fields.get("thread") or path.stem
        closed = fields.get("closed") or path.stem[:15]
        entry = {
            "thread": thread,
            "area": thread.split("-", 1)[0],
            "status": fields.get("status", "open").lower() if fields.get("status") else "open",
            "next": fields.get("next", ""),
            "deadline": parse_deadline(fields.get("deadline", "")),
            "closed": closed,
            "title": title,
            "handoff": path.relative_to(root).as_posix(),
            "no_front_matter": not fields,
        }
        if entry["status"] not in STATUSES:
            entry["status_raw"], entry["status"] = entry["status"], "open"
        per_thread[thread] = per_thread.get(thread, 0) + 1
        previous = threads.get(thread)
        if previous and (previous["closed"], previous["handoff"]) > (closed, entry["handoff"]):
            continue
        threads[thread] = entry
    for thread, entry in threads.items():
        entry["handoffs"] = per_thread[thread]
    return threads, sessions, count


def declined_counts(root: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    try:
        lines = (root / LOG).read_text(encoding="utf-8").splitlines()
    except OSError:
        return counts
    for line in lines:
        try:
            run = json.loads(line)
        except ValueError:
            continue
        for thread in set(run.get("declined", [])):
            counts[thread] = counts.get(thread, 0) + 1
    return counts


def active_briefs(root: Path) -> list[dict]:
    folder = root / ACTIVE
    if not folder.is_dir():
        return []
    now = datetime.now().timestamp()
    briefs = []
    for path in sorted(folder.glob("*.md")):
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        session = re.search(r"^session:\s*(\S+)", text, re.MULTILINE)
        briefs.append({"brief": path.relative_to(root).as_posix(),
                       "session": session.group(1) if session else "",
                       "idle_hours": round((now - path.stat().st_mtime) / 3600, 1)})
    return briefs


# ------------------------------------------------------------- transcripts

def config_dir() -> Path:
    env = os.environ.get("CLAUDE_CONFIG_DIR")
    return Path(env).expanduser() if env else Path.home() / ".claude"


def encode(path: Path) -> str:
    return re.sub(r"[^A-Za-z0-9]", "-", str(path))


def same_path(a: str, b: Path) -> bool:
    try:
        return os.path.normcase(os.path.abspath(a)) == os.path.normcase(str(b))
    except (TypeError, ValueError):
        return False


def first_cwd(path: Path) -> str:
    try:
        with path.open(encoding="utf-8", errors="replace") as handle:
            for _, line in zip(range(200), handle):
                try:
                    cwd = json.loads(line).get("cwd")
                except (ValueError, AttributeError):
                    continue
                if cwd:
                    return cwd
    except OSError:
        pass
    return ""


def transcript_dir(root: Path, projects: Path) -> tuple[Path | None, str]:
    if not projects.is_dir():
        return None, f"no transcript folder at {projects}"
    direct = projects / encode(root)
    if direct.is_dir():
        return direct, "matched by encoded path"
    for folder in projects.iterdir():  # long paths may be encoded differently
        if not folder.is_dir():
            continue
        files = sorted(folder.glob("*.jsonl"), key=lambda f: f.stat().st_mtime, reverse=True)
        if files and same_path(first_cwd(files[0]), root):
            return folder, "matched by cwd"
    return None, "no transcript folder for this project"


def clean(text: str) -> str:
    text = REMINDER.sub("", text).strip()
    return re.sub(r"\s+", " ", text)


def clip(text: str) -> str:
    return text if len(text) <= EXCERPT else text[:EXCERPT - 1] + "…"


def parse_time(raw: str) -> datetime | None:
    try:
        moment = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except (AttributeError, ValueError):
        return None
    return moment if moment.tzinfo else moment.replace(tzinfo=timezone.utc)


def read_transcript(path: Path) -> dict:
    info = {"session": path.stem, "title": "", "first_user": "", "last_user": "",
            "last_assistant": "", "user_turns": 0, "files_written": set(),
            "wrote_handoff": False, "close_started": False, "start": None, "end": None}
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            try:
                record = json.loads(line)
            except ValueError:
                continue
            if not isinstance(record, dict) or record.get("isSidechain"):
                continue
            kind = record.get("type")
            if kind == "custom-title" and record.get("customTitle"):
                info["title"] = str(record["customTitle"])
            elif kind == "summary" and record.get("summary") and not info["title"]:
                info["title"] = str(record["summary"])
            if kind not in ("user", "assistant"):
                continue
            moment = parse_time(record.get("timestamp", ""))
            if moment:
                info["start"] = min(info["start"] or moment, moment)
                info["end"] = max(info["end"] or moment, moment)
            message = record.get("message")
            content = message.get("content") if isinstance(message, dict) else None
            blocks = [{"type": "text", "text": content}] if isinstance(content, str) else content
            if not isinstance(blocks, list):
                continue
            if kind == "user":
                if record.get("isMeta") or record.get("isCompactSummary"):
                    continue
                texts = []
                for block in blocks:
                    if not isinstance(block, dict) or block.get("type") != "text":
                        continue
                    raw = str(block.get("text", ""))
                    command = COMMAND.search(raw)
                    if command and "close-session" in command.group(1):
                        info["close_started"] = True
                    if command:
                        texts.append(command.group(1))
                    elif not raw.lstrip().startswith(("<local-command", "<command-")):
                        texts.append(clean(raw))
                text = " ".join(t for t in texts if t)
                if text:
                    info["user_turns"] += 1
                    info["first_user"] = info["first_user"] or clip(text)
                    info["last_user"] = clip(text)
            else:
                for block in blocks:
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") == "text" and str(block.get("text", "")).strip():
                        info["last_assistant"] = clip(clean(str(block["text"])))
                    elif block.get("type") == "tool_use":
                        args = block.get("input") or {}
                        name = block.get("name", "")
                        if name in WRITE_TOOLS and isinstance(args, dict):
                            target = str(args.get("file_path") or args.get("notebook_path") or "")
                            if target:
                                info["files_written"].add(target)
                                if ".claude/sessions/handoffs/" in target.replace("\\", "/"):
                                    info["wrote_handoff"] = True
                        elif name == "Skill" and "close-session" in json.dumps(args):
                            info["close_started"] = True
    return info


def collect_sessions(folder: Path, days: int, closed_ids: set, exclude: set) -> list[dict]:
    cutoff = datetime.now().timestamp() - days * 86400
    now = datetime.now(timezone.utc)
    sessions = []
    for path in folder.glob("*.jsonl"):  # top level only: subagent logs live deeper
        if path.stem in exclude or path.stat().st_mtime < cutoff:
            continue
        try:
            info = read_transcript(path)
        except OSError:
            continue
        if info["user_turns"] == 0:
            continue
        handoff = info["session"] in closed_ids or info["wrote_handoff"]
        if handoff:
            continue
        idle = (now - info["end"]).total_seconds() / 60 if info["end"] else None
        sessions.append({
            "session": info["session"],
            "title": clip(info["title"] or info["first_user"]),
            "start": info["start"].isoformat(timespec="minutes") if info["start"] else "",
            "end": info["end"].isoformat(timespec="minutes") if info["end"] else "",
            "maybe_running": idle is not None and idle < LIVE_MINUTES,
            "user_turns": info["user_turns"],
            "files_written": len(info["files_written"]),
            "close_started": info["close_started"],
            "last_user": info["last_user"],
            "last_assistant": info["last_assistant"],
            "transcript": path.name,
        })
    sessions.sort(key=lambda s: s["end"], reverse=True)
    return sessions


# ------------------------------------------------------------------ output

def ranked(threads) -> list[dict]:
    """Urgent firm deadlines first (soonest first), then newest handoff first;
    threads declined in two passes or more go last."""
    def urgency(thread: dict) -> tuple:
        deadline = thread.get("deadline") or {}
        urgent = deadline.get("kind") == "firm" and deadline.get("days_left", 99) <= URGENT_DAYS
        return (thread.get("declined", 0) >= 2, not urgent,
                deadline.get("date", "") if urgent else "")
    newest_first = sorted(threads, key=lambda t: (t["closed"], t["handoff"]), reverse=True)
    return sorted(newest_first, key=urgency)  # stable: keeps newest first within a rank


def describe_deadline(deadline: dict | None) -> str:
    if not deadline:
        return ""
    days = deadline["days_left"]
    if deadline["kind"] == "marker":
        return f"marker {deadline['date']}"
    if days < 0:
        return f"FIRM {deadline['date']}, {-days} d late"
    return f"FIRM {deadline['date']}, in {days} d"


def render(report: dict, show_all: bool) -> str:
    out = [f"# Up next — {report['project']}",
           f"{report['handoffs']} handoffs, {len(report['threads'])} threads; "
           f"transcripts: {report['transcripts']}", ""]
    groups = {s: [t for t in report["threads"] if t["status"] == s] for s in STATUSES}
    labels = [("waiting", "Waiting on the user"), ("open", "Open"), ("blocked", "Blocked (third party)")]
    if show_all:
        labels.append(("paused", "Paused"))
    for status, label in labels:
        items = ranked(groups[status])
        out.append(f"## {label} ({len(items)})")
        for t in items:
            extra = [x for x in (describe_deadline(t.get("deadline")),
                                 f"declined in {t['declined']} passes" if t.get("declined") else "",
                                 "no front matter" if t.get("no_front_matter") else "") if x]
            out.append(f"- [{t['area']}] `{t['thread']}` — {t['next'] or '(no next action)'}"
                       f"{' · ' + ' · '.join(extra) if extra else ''} · {t['closed']} · {t['handoff']}")
        out.append("")
    if not show_all:
        out += [f"Paused: {len(groups['paused'])} · closed: {len(groups['closed'])} (use --all to list paused)", ""]
    out.append(f"## Sessions without a handoff ({len(report['sessions'])})")
    for s in report["sessions"]:
        flags = [f for f in ("maybe still running" if s["maybe_running"] else "",
                             "close-session started" if s["close_started"] else "") if f]
        out.append(f"- {s['session'][:8]} · {s['title']} · {s['start']} → {s['end']} · "
                   f"{s['user_turns']} user turns · {s['files_written']} files written"
                   f"{' · ' + ', '.join(flags) if flags else ''}")
        out.append(f"  last user: {s['last_user']}")
        if s["last_assistant"]:
            out.append(f"  last assistant: {s['last_assistant']}")
    out.append("")
    out.append(f"## Working briefs in .claude/sessions/active ({len(report['briefs'])})")
    for b in report["briefs"]:
        out.append(f"- {b['brief']} · idle {b['idle_hours']} h"
                   f"{' · session ' + b['session'][:8] if b['session'] else ''}")
    return "\n".join(out) + "\n"


def scan(args: argparse.Namespace) -> int:
    root = Path(args.project).expanduser().resolve()
    threads, closed_ids, count = collect_threads(root)
    declined = declined_counts(root)
    for thread in threads.values():
        if declined.get(thread["thread"]):
            thread["declined"] = declined[thread["thread"]]
    sessions: list[dict] = []
    if args.no_transcripts:
        status = "skipped (--no-transcripts)"
    else:
        projects = Path(args.projects_dir).expanduser() if args.projects_dir else config_dir() / "projects"
        folder, status = transcript_dir(root, projects)
        if folder:
            exclude = {s.strip() for s in args.exclude_session.split(",") if s.strip()}
            sessions = collect_sessions(folder, args.days, closed_ids, exclude)
            status = f"{status}, last {args.days} days"
    report = {"project": root.name, "handoffs": count, "transcripts": status,
              "threads": ranked(threads.values()), "sessions": sessions,
              "briefs": active_briefs(root)}
    sys.stdout.write(render(report, args.all))
    if args.json:
        Path(args.json).write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


def log(args: argparse.Namespace) -> int:
    root = Path(args.project).expanduser().resolve()
    split = lambda raw: [x.strip() for x in raw.split(",") if x.strip()]
    run = {"date": datetime.now().isoformat(timespec="minutes"), "shown": split(args.shown),
           "launched": split(args.launched), "declined": split(args.declined), "notes": args.note}
    path = root / LOG
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(run, ensure_ascii=False) + "\n")
    print(f"logged pass to {LOG.as_posix()}: {len(run['shown'])} shown, "
          f"{len(run['launched'])} launched, {len(run['declined'])} declined")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_scan = sub.add_parser("scan", help="list threads, unclosed sessions and briefs")
    p_scan.add_argument("--project", default=".", help="project root (default: current folder)")
    p_scan.add_argument("--days", type=int, default=7, help="transcript window in days")
    p_scan.add_argument("--projects-dir", help="Claude Code projects folder (default: <config>/projects)")
    p_scan.add_argument("--exclude-session", default="", help="session ids to skip, comma-separated")
    p_scan.add_argument("--all", action="store_true", help="also list paused threads")
    p_scan.add_argument("--no-transcripts", action="store_true", help="read handoffs only")
    p_scan.add_argument("--json", help="also write the full report as JSON to this file")
    p_log = sub.add_parser("log", help="append one /up-next pass to the run log")
    p_log.add_argument("--project", default=".")
    p_log.add_argument("--shown", default="")
    p_log.add_argument("--launched", default="")
    p_log.add_argument("--declined", default="")
    p_log.add_argument("--note", action="append", default=[])
    args = parser.parse_args()
    return scan(args) if args.cmd == "scan" else log(args)


if __name__ == "__main__":
    sys.exit(main())
