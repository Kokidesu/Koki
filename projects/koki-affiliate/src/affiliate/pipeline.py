"""Orchestration: seed -> keywords -> articles -> static site."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional

from . import affiliate, generate, keywords, render
from .config import Config
from .generate import Article


@dataclass
class Report:
    seed: str
    keywords: List[str]
    articles: List[Article]
    out_dir: str


def run(
    seed: str,
    count: int,
    config: Config,
    *,
    on_event: Optional[Callable[[str], None]] = None,
) -> Report:
    def ev(msg: str) -> None:
        if on_event:
            on_event(msg)

    ev(f"キーワード展開：「{seed}」→ {count}本")
    kws = keywords.expand(seed, count, config)

    articles: List[Article] = []
    seen: set[str] = set()
    for idx, kw in enumerate(kws, 1):
        ev(f"[{idx}/{len(kws)}] 記事生成：{kw}")
        art = generate.generate(kw, config)

        # Ensure a unique slug across the batch.
        base = art.slug or f"post-{idx}"
        slug, k = base, 2
        while slug in seen:
            slug = f"{base}-{k}"
            k += 1
        seen.add(slug)
        art.slug = slug

        art.body_md = affiliate.inject(art.body_md, kw, config)
        articles.append(art)

    ev(f"サイト出力：{config.base_dir}/")
    render.render_site(articles, config)

    return Report(seed=seed, keywords=kws, articles=articles, out_dir=config.base_dir)
