"""Koki command-line interface.

Subcommands:
  koki chat                 Interactive bilingual agent (manages + executes tasks).
  koki ask "..."            One-shot request to the agent.
  koki research "..."       Ask Hono-chan (ほのちゃん): deeply researched answer.
  koki task add "..."       Add a task directly (no LLM).
  koki task list            List tasks.
  koki task show <id>       Show a task and its log.
  koki task done <id>       Mark a task done.
  koki task rm <id>         Delete a task.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

from .db import TaskStore
from .i18n import detect_lang, t
from .tools import ToolBox

console = Console()

_STATUS_STYLE = {
    "todo": "white",
    "in_progress": "yellow",
    "blocked": "red",
    "done": "green",
    "cancelled": "dim",
}


def _print_tasks(tasks, lang: str) -> None:
    if not tasks:
        console.print(f"[dim]{t('no_tasks', lang)}[/dim]")
        return
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("ID", justify="right")
    table.add_column("P")
    table.add_column("Status")
    table.add_column("Title")
    table.add_column("Tags", style="dim")
    pmark = {"urgent": "🔴", "high": "🟠", "medium": "🟡", "low": "⚪"}
    for t_ in tasks:
        table.add_row(
            str(t_.id),
            pmark.get(t_.priority, "?"),
            f"[{_STATUS_STYLE.get(t_.status, 'white')}]{t_.status}[/]",
            t_.title,
            ", ".join(t_.tags),
        )
    console.print(table)


def _build_agent(store: TaskStore, allow_shell: bool):
    lang_text = None
    if not os.environ.get("ANTHROPIC_API_KEY"):
        console.print(f"[red]{t('no_api_key', detect_lang(lang_text))}[/red]")
        sys.exit(1)
    from .agent import Agent

    toolbox = ToolBox(store, allow_shell=allow_shell)
    return Agent(toolbox)


def _hono_request(user: str) -> str | None:
    """If the message invokes Hono-chan, return the bare question; else None.

    Triggers: '/hono ...', '/research ...', or a message addressed to 'ほのちゃん'
    / 'hono' (e.g. 'ほのちゃん、〜教えて').
    """
    text = user.strip()
    low = text.lower()
    for prefix in ("/hono", "/research", "hono:", "ほのちゃん:"):
        if low.startswith(prefix):
            return text[len(prefix):].lstrip(" 　,、:：").strip() or text
    for name in ("ほのちゃん", "ほの "):
        if text.startswith(name):
            return text[len(name):].lstrip(" 　,、:：").strip() or text
    return None


def _on_tool(name: str, args: dict) -> None:
    preview = ", ".join(f"{k}={v}" for k, v in list(args.items())[:3])
    console.print(f"[dim]→ {name}({preview})[/dim]")


def cmd_chat(args, store: TaskStore) -> None:
    agent = _build_agent(store, allow_shell=not args.no_shell)
    lang = detect_lang()
    console.print(f"[bold cyan]Koki[/bold cyan] — {t('welcome', lang)}")
    console.print("[dim](exit / quit / 終了 to leave)[/dim]\n")
    while True:
        try:
            user = console.input("[bold green]you ›[/bold green] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print()
            break
        if user.lower() in {"exit", "quit", ":q"} or user in {"終了", "おわり"}:
            console.print(f"[dim]{t('bye', detect_lang(user))}[/dim]")
            break
        if not user:
            continue
        # Route to Hono-chan when the user invokes her by name or with /hono.
        hono_q = _hono_request(user)
        if hono_q is not None:
            with console.status("[dim]ほのちゃんが調べてます… / Hono-chan is researching…[/dim]"):
                reply = agent.research(hono_q, on_tool=_on_tool)
            console.print(f"\n[bold magenta]ほのちゃん ›[/bold magenta] {reply}\n")
            continue
        with console.status(f"[dim]{t('thinking', detect_lang(user))}[/dim]"):
            reply = agent.send(user, on_tool=_on_tool)
        console.print(f"\n[bold cyan]Koki ›[/bold cyan] {reply}\n")


def cmd_ask(args, store: TaskStore) -> None:
    agent = _build_agent(store, allow_shell=not args.no_shell)
    reply = agent.send(args.prompt, on_tool=_on_tool)
    console.print(reply)


def cmd_research(args, store: TaskStore) -> None:
    """Ask Hono-chan (ほのちゃん): a deeply researched, super-specific answer."""
    agent = _build_agent(store, allow_shell=False)
    lang = detect_lang(args.question)
    with console.status(f"[dim]ほのちゃんが調べてます… / Hono-chan is researching…[/dim]"):
        reply = agent.research(args.question, on_tool=_on_tool)
    console.print(f"\n[bold magenta]ほのちゃん ›[/bold magenta] {reply}\n")


def cmd_plan(args, store: TaskStore) -> None:
    agent = _build_agent(store, allow_shell=not args.no_shell)
    with console.status(f"[dim]{t('thinking', detect_lang(args.goal))}[/dim]"):
        reply = agent.plan(args.goal, on_tool=_on_tool)
    console.print(reply)


def cmd_run(args, store: TaskStore) -> None:
    agent = _build_agent(store, allow_shell=not args.no_shell)
    with console.status("[dim]working…[/dim]"):
        reply = agent.run_tasks(on_tool=_on_tool, only_id=args.id)
    console.print(reply)


def cmd_gh(args, store: TaskStore) -> None:
    from . import github_sync

    lang = detect_lang()
    try:
        if args.gh_cmd == "pull":
            counts = github_sync.pull_issues(store, args.repo, state=args.state)
            console.print(f"[green]✓[/green] pulled: created={counts['created']} updated={counts['updated']}")
            _print_tasks(store.list(), lang)
        elif args.gh_cmd == "push":
            res = github_sync.push_task(store, args.repo, args.id)
            console.print(f"[green]✓[/green] created issue #{res['issue_number']}: {res['url']}")
    except github_sync.GitHubError as e:
        console.print(f"[red]GitHub error:[/red] {e}")
        sys.exit(1)


def cmd_task(args, store: TaskStore) -> None:
    lang = detect_lang(getattr(args, "title", None))
    if args.task_cmd == "add":
        task = store.add(
            title=args.title,
            description=args.description or "",
            priority=args.priority,
            tags=args.tags.split(",") if args.tags else [],
        )
        console.print(f"[green]{t('task_added', lang)}[/green] #{task.id}: {task.title}")
    elif args.task_cmd == "list":
        _print_tasks(store.list(status=args.status, tag=args.tag), lang)
    elif args.task_cmd == "show":
        task = store.get(args.id)
        if not task:
            console.print(f"[red]{t('not_found', lang)}[/red]")
            return
        console.print(f"[bold]#{task.id} {task.title}[/bold]  ({task.status}) {task.priority}")
        if task.description:
            console.print(task.description)
        if task.tags:
            console.print(f"[dim]tags: {', '.join(task.tags)}[/dim]")
        logs = store.logs(task.id)
        if logs:
            console.print("[bold]log:[/bold]")
            for entry in logs:
                console.print(f"  • {entry['note']}")
    elif args.task_cmd == "done":
        task = store.update(args.id, status="done")
        msg = t("task_updated", lang) if task else t("not_found", lang)
        console.print(f"[green]{msg}[/green]" if task else f"[red]{msg}[/red]")
    elif args.task_cmd == "rm":
        ok = store.delete(args.id)
        msg = t("task_deleted", lang) if ok else t("not_found", lang)
        console.print(f"[green]{msg}[/green]" if ok else f"[red]{msg}[/red]")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="koki", description="Koki — bilingual task-managing & executing agent")
    p.add_argument("--db", help="Path to the task database.")
    sub = p.add_subparsers(dest="cmd", required=True)

    pc = sub.add_parser("chat", help="Interactive agent session.")
    pc.add_argument("--no-shell", action="store_true", help="Disable shell execution.")
    pc.set_defaults(func=cmd_chat)

    pa = sub.add_parser("ask", help="One-shot request to the agent.")
    pa.add_argument("prompt")
    pa.add_argument("--no-shell", action="store_true")
    pa.set_defaults(func=cmd_ask)

    pres = sub.add_parser(
        "research",
        aliases=["hono", "ask-hono"],
        help="Ask Hono-chan (ほのちゃん): deeply researched, super-specific answer.",
    )
    pres.add_argument("question")
    pres.set_defaults(func=cmd_research)

    pp = sub.add_parser("plan", help="Decompose a goal into tasks (LLM).")
    pp.add_argument("goal")
    pp.add_argument("--no-shell", action="store_true")
    pp.set_defaults(func=cmd_plan)

    pr = sub.add_parser("run", help="Autonomously execute outstanding tasks (LLM).")
    pr.add_argument("--id", type=int, help="Run a single task by id.")
    pr.add_argument("--no-shell", action="store_true")
    pr.set_defaults(func=cmd_run)

    pg = sub.add_parser("gh", help="GitHub Issues sync.")
    gsub = pg.add_subparsers(dest="gh_cmd", required=True)
    gp = gsub.add_parser("pull", help="Import issues into tasks.")
    gp.add_argument("repo", help="owner/name")
    gp.add_argument("--state", default="open", choices=["open", "closed", "all"])
    gpush = gsub.add_parser("push", help="Create a GitHub issue from a task.")
    gpush.add_argument("repo", help="owner/name")
    gpush.add_argument("id", type=int)
    pg.set_defaults(func=cmd_gh)

    pt = sub.add_parser("task", help="Direct task DB operations (no LLM).")
    tsub = pt.add_subparsers(dest="task_cmd", required=True)
    ta = tsub.add_parser("add")
    ta.add_argument("title")
    ta.add_argument("-d", "--description")
    ta.add_argument("-p", "--priority", default="medium", choices=["low", "medium", "high", "urgent"])
    ta.add_argument("--tags", help="Comma-separated tags.")
    tl = tsub.add_parser("list")
    tl.add_argument("--status", choices=["todo", "in_progress", "blocked", "done", "cancelled"])
    tl.add_argument("--tag")
    tsh = tsub.add_parser("show")
    tsh.add_argument("id", type=int)
    td = tsub.add_parser("done")
    td.add_argument("id", type=int)
    tr = tsub.add_parser("rm")
    tr.add_argument("id", type=int)
    pt.set_defaults(func=cmd_task)

    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    store = TaskStore(Path(args.db).expanduser() if args.db else None)
    try:
        args.func(args, store)
    finally:
        store.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
