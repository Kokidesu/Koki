"""Tests for GitHub sync logic with the network layer mocked out."""

import pytest

from koki import github_sync
from koki.db import TaskStore


@pytest.fixture
def store(tmp_path):
    s = TaskStore(tmp_path / "t.db")
    yield s
    s.close()


def test_token_required(store, monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)
    with pytest.raises(github_sync.GitHubError):
        github_sync.pull_issues(store, "owner/repo")


def test_pull_creates_and_updates(store, monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "x")
    pages = {
        1: [
            {"number": 1, "title": "Issue one", "body": "body", "state": "open",
             "labels": [{"name": "bug"}]},
            {"number": 2, "title": "A PR", "body": "", "state": "open",
             "labels": [], "pull_request": {}},
        ],
        2: [],
    }

    def fake_request(method, path, token, payload=None):
        page = int(path.split("&page=")[1])
        return pages[page]

    monkeypatch.setattr(github_sync, "_request", fake_request)
    counts = github_sync.pull_issues(store, "owner/repo")
    assert counts["created"] == 1  # PR skipped
    tasks = store.list()
    assert len(tasks) == 1
    assert "gh:1" in tasks[0].tags
    assert "bug" in tasks[0].tags

    # Second pull updates rather than duplicates.
    counts2 = github_sync.pull_issues(store, "owner/repo")
    assert counts2["updated"] == 1
    assert len(store.list()) == 1


def test_push_task_links_issue(store, monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "x")
    task = store.add("do a thing", description="d", tags=["feature"])

    def fake_request(method, path, token, payload=None):
        assert method == "POST"
        return {"number": 42, "html_url": "https://github.com/o/r/issues/42"}

    monkeypatch.setattr(github_sync, "_request", fake_request)
    res = github_sync.push_task(store, "owner/repo", task.id)
    assert res["issue_number"] == 42
    assert "gh:42" in store.get(task.id).tags

    # Pushing again should refuse (already linked).
    with pytest.raises(github_sync.GitHubError):
        github_sync.push_task(store, "owner/repo", task.id)
