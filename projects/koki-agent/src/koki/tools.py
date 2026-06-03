"""Tool definitions and dispatch for the Koki agent.

Each tool is exposed to Claude via the Messages API `tools` parameter. The
handlers operate on a TaskStore (for task management) and the local shell /
filesystem (for actually *executing* tasks).
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Callable

from .db import PRIORITIES, STATUSES, TaskStore

# JSON schema for every tool exposed to the model.
TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "name": "add_task",
        "description": "Create a new task in the task database. Use when the user describes work to be tracked.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Short title of the task."},
                "description": {"type": "string", "description": "Detailed description / acceptance criteria."},
                "priority": {"type": "string", "enum": list(PRIORITIES)},
                "tags": {"type": "array", "items": {"type": "string"}},
                "depends_on": {"type": "array", "items": {"type": "integer"}, "description": "IDs of prerequisite tasks."},
            },
            "required": ["title"],
        },
    },
    {
        "name": "list_tasks",
        "description": "List tasks, optionally filtered by status or tag.",
        "input_schema": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": list(STATUSES)},
                "tag": {"type": "string"},
            },
        },
    },
    {
        "name": "get_task",
        "description": "Fetch a single task with its full execution log.",
        "input_schema": {
            "type": "object",
            "properties": {"id": {"type": "integer"}},
            "required": ["id"],
        },
    },
    {
        "name": "update_task",
        "description": "Update fields of an existing task (status, priority, title, description, tags, depends_on).",
        "input_schema": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "title": {"type": "string"},
                "description": {"type": "string"},
                "status": {"type": "string", "enum": list(STATUSES)},
                "priority": {"type": "string", "enum": list(PRIORITIES)},
                "tags": {"type": "array", "items": {"type": "string"}},
                "depends_on": {"type": "array", "items": {"type": "integer"}},
            },
            "required": ["id"],
        },
    },
    {
        "name": "delete_task",
        "description": "Delete a task permanently.",
        "input_schema": {
            "type": "object",
            "properties": {"id": {"type": "integer"}},
            "required": ["id"],
        },
    },
    {
        "name": "log_task",
        "description": "Append a progress note to a task's execution log.",
        "input_schema": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "note": {"type": "string"},
            },
            "required": ["id", "note"],
        },
    },
    {
        "name": "run_shell",
        "description": (
            "Execute a shell command to actually carry out a task (run scripts, build, test, "
            "manipulate files). Returns stdout, stderr and exit code. Use cautiously."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string"},
                "cwd": {"type": "string", "description": "Working directory (optional)."},
            },
            "required": ["command"],
        },
    },
    {
        "name": "read_file",
        "description": "Read a text file from disk.",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Write (create or overwrite) a text file on disk.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["path", "content"],
        },
    },
]


class ToolBox:
    """Holds state (the task store) and dispatches tool calls by name."""

    def __init__(self, store: TaskStore, allow_shell: bool = True, shell_root: Path | None = None):
        self.store = store
        self.allow_shell = allow_shell
        self.shell_root = shell_root or Path.cwd()
        self._handlers: dict[str, Callable[..., Any]] = {
            "add_task": self._add_task,
            "list_tasks": self._list_tasks,
            "get_task": self._get_task,
            "update_task": self._update_task,
            "delete_task": self._delete_task,
            "log_task": self._log_task,
            "run_shell": self._run_shell,
            "read_file": self._read_file,
            "write_file": self._write_file,
        }

    def dispatch(self, name: str, args: dict[str, Any]) -> str:
        handler = self._handlers.get(name)
        if not handler:
            return json.dumps({"error": f"unknown tool: {name}"})
        try:
            result = handler(**args)
        except TypeError as e:
            return json.dumps({"error": f"bad arguments: {e}"})
        except Exception as e:  # surface errors back to the model
            return json.dumps({"error": str(e)})
        return json.dumps(result, ensure_ascii=False, default=str)

    # --- task tools -----------------------------------------------------

    def _add_task(self, title, description="", priority="medium", tags=None, depends_on=None):
        task = self.store.add(title, description, priority, tags, depends_on)
        return task.to_dict()

    def _list_tasks(self, status=None, tag=None):
        return [t.to_dict() for t in self.store.list(status=status, tag=tag)]

    def _get_task(self, id):
        task = self.store.get(id)
        if not task:
            return {"error": "task not found", "id": id}
        d = task.to_dict()
        d["log"] = self.store.logs(id)
        return d

    def _update_task(self, id, **fields):
        task = self.store.update(id, **fields)
        if not task:
            return {"error": "task not found", "id": id}
        return task.to_dict()

    def _delete_task(self, id):
        ok = self.store.delete(id)
        return {"deleted": ok, "id": id}

    def _log_task(self, id, note):
        if not self.store.get(id):
            return {"error": "task not found", "id": id}
        self.store.log(id, note)
        return {"ok": True, "id": id}

    # --- execution tools ------------------------------------------------

    def _run_shell(self, command, cwd=None):
        if not self.allow_shell:
            return {"error": "shell execution is disabled (run with --allow-shell)"}
        proc = subprocess.run(
            command,
            shell=True,
            cwd=cwd or str(self.shell_root),
            capture_output=True,
            text=True,
            timeout=600,
        )
        return {
            "exit_code": proc.returncode,
            "stdout": proc.stdout[-8000:],
            "stderr": proc.stderr[-4000:],
        }

    def _read_file(self, path):
        p = Path(path).expanduser()
        return {"path": str(p), "content": p.read_text()[:20000]}

    def _write_file(self, path, content):
        p = Path(path).expanduser()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
        return {"path": str(p), "bytes": len(content.encode())}
