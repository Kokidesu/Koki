"""SQLite-backed task store for Koki.

Tasks are the unit of work the agent manages and executes. The schema is
intentionally small but expressive enough to track lifecycle, priority,
dependencies and an execution log.
"""

from __future__ import annotations

import json
import os
import sqlite3
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

# Allowed lifecycle states for a task.
STATUSES = ("todo", "in_progress", "blocked", "done", "cancelled")
PRIORITIES = ("low", "medium", "high", "urgent")


def default_db_path() -> Path:
    """Resolve the DB path, honouring KOKI_DB env override."""
    env = os.environ.get("KOKI_DB")
    if env:
        return Path(env).expanduser()
    base = Path(os.environ.get("KOKI_HOME", Path.home() / ".koki"))
    return base / "koki.db"


@dataclass
class Task:
    id: int
    title: str
    description: str
    status: str
    priority: str
    tags: list[str] = field(default_factory=list)
    depends_on: list[int] = field(default_factory=list)
    created_at: float = 0.0
    updated_at: float = 0.0

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Task":
        return cls(
            id=row["id"],
            title=row["title"],
            description=row["description"] or "",
            status=row["status"],
            priority=row["priority"],
            tags=json.loads(row["tags"] or "[]"),
            depends_on=json.loads(row["depends_on"] or "[]"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "tags": self.tags,
            "depends_on": self.depends_on,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class TaskStore:
    def __init__(self, path: Optional[Path] = None):
        self.path = path or default_db_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self._migrate()

    def _migrate(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                status TEXT NOT NULL DEFAULT 'todo',
                priority TEXT NOT NULL DEFAULT 'medium',
                tags TEXT DEFAULT '[]',
                depends_on TEXT DEFAULT '[]',
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS task_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                note TEXT NOT NULL,
                created_at REAL NOT NULL,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
            );
            """
        )
        self.conn.commit()

    # --- CRUD -----------------------------------------------------------

    def add(
        self,
        title: str,
        description: str = "",
        priority: str = "medium",
        tags: Optional[list[str]] = None,
        depends_on: Optional[list[int]] = None,
    ) -> Task:
        if priority not in PRIORITIES:
            raise ValueError(f"invalid priority: {priority}")
        now = time.time()
        cur = self.conn.execute(
            """INSERT INTO tasks (title, description, status, priority, tags, depends_on, created_at, updated_at)
               VALUES (?, ?, 'todo', ?, ?, ?, ?, ?)""",
            (
                title,
                description,
                priority,
                json.dumps(tags or [], ensure_ascii=False),
                json.dumps(depends_on or []),
                now,
                now,
            ),
        )
        self.conn.commit()
        return self.get(cur.lastrowid)  # type: ignore[arg-type]

    def get(self, task_id: int) -> Optional[Task]:
        row = self.conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return Task.from_row(row) if row else None

    def list(
        self,
        status: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> list[Task]:
        q = "SELECT * FROM tasks"
        conds, args = [], []
        if status:
            conds.append("status = ?")
            args.append(status)
        if conds:
            q += " WHERE " + " AND ".join(conds)
        q += " ORDER BY CASE priority WHEN 'urgent' THEN 0 WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END, id"
        tasks = [Task.from_row(r) for r in self.conn.execute(q, args).fetchall()]
        if tag:
            tasks = [t for t in tasks if tag in t.tags]
        return tasks

    def update(self, task_id: int, **fields: Any) -> Optional[Task]:
        task = self.get(task_id)
        if not task:
            return None
        allowed = {"title", "description", "status", "priority", "tags", "depends_on"}
        sets, args = [], []
        for k, v in fields.items():
            if k not in allowed or v is None:
                continue
            if k == "status" and v not in STATUSES:
                raise ValueError(f"invalid status: {v}")
            if k == "priority" and v not in PRIORITIES:
                raise ValueError(f"invalid priority: {v}")
            if k in ("tags", "depends_on"):
                v = json.dumps(v, ensure_ascii=False)
            sets.append(f"{k} = ?")
            args.append(v)
        if not sets:
            return task
        sets.append("updated_at = ?")
        args.append(time.time())
        args.append(task_id)
        self.conn.execute(f"UPDATE tasks SET {', '.join(sets)} WHERE id = ?", args)
        self.conn.commit()
        return self.get(task_id)

    def delete(self, task_id: int) -> bool:
        cur = self.conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.conn.commit()
        return cur.rowcount > 0

    # --- Execution log --------------------------------------------------

    def log(self, task_id: int, note: str) -> None:
        self.conn.execute(
            "INSERT INTO task_log (task_id, note, created_at) VALUES (?, ?, ?)",
            (task_id, note, time.time()),
        )
        self.conn.commit()

    def logs(self, task_id: int) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT note, created_at FROM task_log WHERE task_id = ? ORDER BY id",
            (task_id,),
        ).fetchall()
        return [{"note": r["note"], "created_at": r["created_at"]} for r in rows]

    def close(self) -> None:
        self.conn.close()
