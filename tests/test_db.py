"""Unit tests for the SQLite task store."""

import pytest

from koki.db import TaskStore


@pytest.fixture
def store(tmp_path):
    s = TaskStore(tmp_path / "test.db")
    yield s
    s.close()


def test_add_and_get(store):
    task = store.add("テスト課題", description="desc", priority="high", tags=["a", "b"])
    assert task.id == 1
    assert task.title == "テスト課題"
    assert task.status == "todo"
    assert task.priority == "high"
    assert task.tags == ["a", "b"]
    fetched = store.get(task.id)
    assert fetched is not None
    assert fetched.title == task.title


def test_invalid_priority(store):
    with pytest.raises(ValueError):
        store.add("bad", priority="nope")


def test_list_orders_by_priority(store):
    store.add("low one", priority="low")
    store.add("urgent one", priority="urgent")
    store.add("medium one", priority="medium")
    titles = [t.title for t in store.list()]
    assert titles[0] == "urgent one"
    assert titles[-1] == "low one"


def test_list_filters(store):
    store.add("a", tags=["x"])
    store.add("b", tags=["y"])
    t = store.add("c")
    store.update(t.id, status="done")
    assert len(store.list(status="done")) == 1
    assert len(store.list(tag="x")) == 1


def test_update_validates_status(store):
    t = store.add("x")
    with pytest.raises(ValueError):
        store.update(t.id, status="invalid")
    updated = store.update(t.id, status="in_progress", priority="urgent")
    assert updated.status == "in_progress"
    assert updated.priority == "urgent"


def test_update_missing_returns_none(store):
    assert store.update(999, status="done") is None


def test_delete(store):
    t = store.add("x")
    assert store.delete(t.id) is True
    assert store.get(t.id) is None
    assert store.delete(t.id) is False


def test_logs(store):
    t = store.add("x")
    store.log(t.id, "started")
    store.log(t.id, "finished")
    logs = store.logs(t.id)
    assert [l["note"] for l in logs] == ["started", "finished"]
