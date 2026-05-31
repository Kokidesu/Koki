"""Lightweight bilingual (Japanese / English) message helper.

Koki detects the preferred language from the KOKI_LANG env var, falling back
to a simple heuristic on the user's input (presence of Japanese characters).
The agent's *responses* are driven by the system prompt, but CLI chrome and
status messages use this table so the tool feels native in both languages.
"""

from __future__ import annotations

import os
import re

_JP_RE = re.compile(r"[぀-ヿ㐀-䶿一-鿿]")

MESSAGES = {
    "welcome": {
        "ja": "Koki エージェントへようこそ。課題の管理から実行までお手伝いします。",
        "en": "Welcome to Koki. I manage and execute your tasks end to end.",
    },
    "no_tasks": {
        "ja": "登録されている課題はありません。",
        "en": "No tasks registered yet.",
    },
    "task_added": {
        "ja": "課題を追加しました",
        "en": "Task added",
    },
    "task_updated": {
        "ja": "課題を更新しました",
        "en": "Task updated",
    },
    "task_deleted": {
        "ja": "課題を削除しました",
        "en": "Task deleted",
    },
    "not_found": {
        "ja": "課題が見つかりません",
        "en": "Task not found",
    },
    "no_api_key": {
        "ja": "環境変数 ANTHROPIC_API_KEY が設定されていません。",
        "en": "ANTHROPIC_API_KEY environment variable is not set.",
    },
    "thinking": {
        "ja": "考え中…",
        "en": "Thinking…",
    },
    "bye": {
        "ja": "またお呼びください。",
        "en": "See you next time.",
    },
}


def detect_lang(text: str | None = None) -> str:
    """Return 'ja' or 'en'. Env var wins; otherwise sniff the text."""
    env = os.environ.get("KOKI_LANG", "").lower()
    if env.startswith("ja"):
        return "ja"
    if env.startswith("en"):
        return "en"
    if text and _JP_RE.search(text):
        return "ja"
    return "en"


def t(key: str, lang: str) -> str:
    entry = MESSAGES.get(key, {})
    return entry.get(lang) or entry.get("en") or key
