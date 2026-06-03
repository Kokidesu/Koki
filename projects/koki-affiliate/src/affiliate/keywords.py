"""Seed keyword -> long-tail keyword expansion."""

from __future__ import annotations

from typing import List

from . import llm
from .config import Config

_SUFFIXES = [
    "おすすめ",
    "比較",
    "ランキング",
    "選び方",
    "初心者向け",
    "安い",
    "デメリット",
    "口コミ",
    "コスパ",
    "人気",
]


def expand(seed: str, count: int, config: Config) -> List[str]:
    """Expand a seed into `count` long-tail keywords (Claude or fallback)."""
    seed = seed.strip()
    if not seed:
        return []
    if llm.have_llm():
        try:
            return _expand_llm(seed, count, config)
        except Exception:
            pass
    return _expand_fallback(seed, count)


def _expand_fallback(seed: str, count: int) -> List[str]:
    out: List[str] = []
    for suffix in _SUFFIXES:
        if len(out) >= count:
            break
        out.append(f"{seed} {suffix}")
    i = 1
    while len(out) < count:
        out.append(f"{seed} まとめ{i}")
        i += 1
    return out[:count]


def _expand_llm(seed: str, count: int, config: Config) -> List[str]:
    prompt = (
        f"アフィリエイトブログのために、シードキーワード「{seed}」から検索流入が"
        f"見込めるロングテールキーワードを{count}個提案してください。"
        f"各行に1個ずつ、キーワードのみを出力し、番号・記号・説明は付けないでください。"
    )
    text = llm.complete(prompt, model=config.model, max_tokens=600)
    lines = [ln.strip(" 　-・*0123456789.") for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]
    return (lines or _expand_fallback(seed, count))[:count]
