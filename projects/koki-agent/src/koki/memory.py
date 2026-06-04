"""Hono-chan's research memory.

A tiny append-only store of past research Q&A so Hono-chan gets smarter over
time: before answering, she recalls the most relevant past notes and folds them
into her context; after answering, she saves the new finding.

Storage is a JSONL file (one record per line) at ~/.koki/hono_memory.jsonl by
default, override with KOKI_MEMORY_PATH.
"""

from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Any

_STOPWORDS = {
    "the", "a", "an", "of", "to", "and", "or", "is", "are", "in", "on", "for",
    "what", "how", "why", "when", "who", "with", "について", "とは", "って",
    "を", "の", "が", "は", "に", "で", "と", "も", "教えて", "ですか",
}


def _default_path() -> Path:
    env = os.environ.get("KOKI_MEMORY_PATH")
    if env:
        return Path(env).expanduser()
    return Path.home() / ".koki" / "hono_memory.jsonl"


def _tokens(text: str) -> set[str]:
    # Split on non-word runs; keep CJK as individual chars for rough overlap.
    words = re.findall(r"[A-Za-z0-9]+", text.lower())
    cjk = re.findall(r"[぀-ヿ一-鿿]", text)
    toks = {w for w in words if w not in _STOPWORDS and len(w) > 1}
    toks |= {c for c in cjk if c not in _STOPWORDS}
    return toks


class HonoMemory:
    def __init__(self, path: Path | None = None):
        self.path = path or _default_path()

    def _read_all(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        records = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return records

    def add(self, question: str, answer: str, sources: list[str]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "ts": time.time(),
            "date": time.strftime("%Y-%m-%d %H:%M", time.localtime()),
            "question": question,
            "answer": answer,
            "sources": sources,
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def recall(self, question: str, limit: int = 3) -> list[dict[str, Any]]:
        """Return the past records most relevant to `question` by token overlap."""
        records = self._read_all()
        if not records:
            return []
        q_tokens = _tokens(question)
        if not q_tokens:
            return records[-limit:]
        scored = []
        for rec in records:
            rec_tokens = _tokens(rec.get("question", "") + " " + rec.get("answer", ""))
            overlap = len(q_tokens & rec_tokens)
            if overlap:
                scored.append((overlap, rec.get("ts", 0), rec))
        scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
        return [rec for _, _, rec in scored[:limit]]

    def as_context(self, question: str, limit: int = 3) -> str:
        """Render relevant past research as a context block, or '' if none."""
        hits = self.recall(question, limit=limit)
        if not hits:
            return ""
        lines = ["[Past research notes — your own earlier findings, reuse if relevant]"]
        for rec in hits:
            ans = rec.get("answer", "").strip()
            if len(ans) > 600:
                ans = ans[:600] + "…"
            lines.append(f"- ({rec.get('date', '?')}) Q: {rec.get('question', '')}\n  A: {ans}")
        return "\n".join(lines)
