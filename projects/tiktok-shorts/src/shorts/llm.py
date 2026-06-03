"""Claude 呼び出しの薄いラッパ。"""
from __future__ import annotations

import json
import os
import re


def _model() -> str:
    return os.environ.get("SHORTS_MODEL", "claude-sonnet-4-6")


def _client():
    try:
        from anthropic import Anthropic
    except ImportError as e:  # pragma: no cover
        raise RuntimeError("anthropic が未インストールです: pip install anthropic") from e
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError("ANTHROPIC_API_KEY が未設定です（.env を確認）")
    return Anthropic()


def complete(system: str, prompt: str, max_tokens: int = 1500, temperature: float = 0.8) -> str:
    msg = _client().messages.create(
        model=_model(),
        max_tokens=max_tokens,
        temperature=temperature,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(b.text for b in msg.content if getattr(b, "type", None) == "text")


def complete_json(system: str, prompt: str, **kw):
    return _extract_json(complete(system, prompt, **kw))


def _extract_json(text: str):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n", "", text)
        text = re.sub(r"\n```$", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = re.search(r"[\[{]", text)
    if m:
        sub = text[m.start():]
        for end in range(len(sub), 0, -1):
            try:
                return json.loads(sub[:end])
            except json.JSONDecodeError:
                continue
    raise ValueError("モデル出力からJSONを抽出できませんでした")
