"""Persist generated articles as JSON so the site accumulates over time.

Each article is one JSON file under the content directory, keyed by slug.
This is the durable record; the HTML in `base_dir` is rebuilt from it.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import List, Set

from .generate import Article


def save_article(article: Article, content_dir: str) -> str:
    d = Path(content_dir)
    d.mkdir(parents=True, exist_ok=True)
    path = d / f"{article.slug}.json"
    path.write_text(
        json.dumps(asdict(article), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return str(path)


def load_all(content_dir: str) -> List[Article]:
    d = Path(content_dir)
    if not d.exists():
        return []
    articles: List[Article] = []
    for f in d.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            articles.append(Article(**data))
        except Exception:
            continue
    # Newest first (ISO date sorts lexically), tie-break by slug.
    articles.sort(key=lambda a: (a.date, a.slug), reverse=True)
    return articles


def existing_slugs(content_dir: str) -> Set[str]:
    return {a.slug for a in load_all(content_dir)}
