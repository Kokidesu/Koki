"""Optional GitHub Issues <-> Koki task synchronisation.

Uses only the standard library (urllib) so Koki stays dependency-light.
Requires a GITHUB_TOKEN env var with `repo` scope. The repository is given
as "owner/name".

Mapping:
  - Each open GitHub issue becomes (or updates) a Koki task tagged `gh:<number>`.
  - Issue title -> task title, body -> description, labels -> tags.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Optional

from .db import TaskStore

API = "https://api.github.com"


class GitHubError(RuntimeError):
    pass


def _request(method: str, path: str, token: str, payload: Optional[dict] = None) -> Any:
    url = path if path.startswith("http") else f"{API}{path}"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "koki-agent")
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode()
            return json.loads(body) if body else None
    except urllib.error.HTTPError as e:
        raise GitHubError(f"GitHub API {e.code}: {e.read().decode()[:300]}") from e


def _token() -> str:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise GitHubError("GITHUB_TOKEN (or GH_TOKEN) env var is required for GitHub sync.")
    return token


def _gh_tag(number: int) -> str:
    return f"gh:{number}"


def _find_task_by_issue(store: TaskStore, number: int):
    tag = _gh_tag(number)
    for t in store.list():
        if tag in t.tags:
            return t
    return None


def pull_issues(store: TaskStore, repo: str, state: str = "open") -> dict[str, int]:
    """Import GitHub issues into the task store. Returns counts."""
    token = _token()
    created = updated = 0
    page = 1
    while True:
        issues = _request("GET", f"/repos/{repo}/issues?state={state}&per_page=50&page={page}", token)
        if not issues:
            break
        for issue in issues:
            if "pull_request" in issue:  # skip PRs
                continue
            number = issue["number"]
            labels = [lbl["name"] for lbl in issue.get("labels", [])]
            tags = labels + [_gh_tag(number)]
            existing = _find_task_by_issue(store, number)
            status = "done" if issue["state"] == "closed" else "todo"
            if existing:
                store.update(
                    existing.id,
                    title=issue["title"],
                    description=issue.get("body") or "",
                    tags=tags,
                    status="done" if issue["state"] == "closed" else existing.status,
                )
                updated += 1
            else:
                store.add(
                    title=issue["title"],
                    description=issue.get("body") or "",
                    priority="medium",
                    tags=tags,
                )
                if status == "done":
                    t = _find_task_by_issue(store, number)
                    if t:
                        store.update(t.id, status="done")
                created += 1
        page += 1
    return {"created": created, "updated": updated}


def push_task(store: TaskStore, repo: str, task_id: int) -> dict[str, Any]:
    """Create a GitHub issue from a Koki task that isn't linked yet."""
    token = _token()
    task = store.get(task_id)
    if not task:
        raise GitHubError(f"task {task_id} not found")
    for tag in task.tags:
        if tag.startswith("gh:"):
            raise GitHubError(f"task {task_id} is already linked to issue #{tag[3:]}")
    labels = [t for t in task.tags if not t.startswith("gh:")]
    issue = _request(
        "POST",
        f"/repos/{repo}/issues",
        token,
        {"title": task.title, "body": task.description, "labels": labels},
    )
    store.update(task_id, tags=task.tags + [_gh_tag(issue["number"])])
    return {"issue_number": issue["number"], "url": issue["html_url"]}
