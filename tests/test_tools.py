"""Unit tests for the ToolBox dispatch layer."""

import json

import pytest

from koki.db import TaskStore
from koki.tools import TOOL_SCHEMAS, ToolBox


@pytest.fixture
def box(tmp_path):
    store = TaskStore(tmp_path / "t.db")
    yield ToolBox(store, allow_shell=True, shell_root=tmp_path)
    store.close()


def _call(box, name, **args):
    return json.loads(box.dispatch(name, args))


def test_schemas_have_required_fields():
    for s in TOOL_SCHEMAS:
        assert "name" in s and "description" in s and "input_schema" in s


def test_add_and_list_task(box):
    created = _call(box, "add_task", title="やること", priority="high")
    assert created["id"] == 1
    listed = _call(box, "list_tasks")
    assert len(listed) == 1
    assert listed[0]["title"] == "やること"


def test_get_task_includes_log(box):
    _call(box, "add_task", title="x")
    _call(box, "log_task", id=1, note="hello")
    got = _call(box, "get_task", id=1)
    assert got["log"][0]["note"] == "hello"


def test_update_task(box):
    _call(box, "add_task", title="x")
    updated = _call(box, "update_task", id=1, status="done")
    assert updated["status"] == "done"


def test_unknown_tool(box):
    assert "error" in _call(box, "does_not_exist")


def test_bad_arguments(box):
    assert "error" in _call(box, "add_task")  # missing required title


def test_run_shell(box):
    out = _call(box, "run_shell", command="echo hi")
    assert out["exit_code"] == 0
    assert "hi" in out["stdout"]


def test_run_shell_disabled(tmp_path):
    store = TaskStore(tmp_path / "t.db")
    box = ToolBox(store, allow_shell=False)
    out = json.loads(box.dispatch("run_shell", {"command": "echo hi"}))
    assert "error" in out
    store.close()


def test_read_write_file(box, tmp_path):
    p = tmp_path / "f.txt"
    _call(box, "write_file", path=str(p), content="データ")
    got = _call(box, "read_file", path=str(p))
    assert got["content"] == "データ"
