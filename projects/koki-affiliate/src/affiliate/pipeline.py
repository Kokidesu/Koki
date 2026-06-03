"""Orchestration: seed(s) -> new articles -> persist -> rebuild static site.

The pipeline is *accumulating*: each run only generates keywords it hasn't
written before, saves them to the content store, and rebuilds the whole site
from everything stored so far. Run it daily and the site grows.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional, Sequence, Union

from . import affiliate, generate, keywords, render, store
from .config import Config
from .generate import Article


@dataclass
class Report:
    new_articles: List[Article]
    total: int
    out_dir: str


def run(
    seeds: Union[str, Sequence[str]],
    per_run: int,
    config: Config,
    *,
    on_event: Optional[Callable[[str], None]] = None,
) -> Report:
    """Generate up to `per_run` brand-new articles across the given seeds,
    persist them, and rebuild the site from the full content store."""

    def ev(msg: str) -> None:
        if on_event:
            on_event(msg)

    if isinstance(seeds, str):
        seeds = [seeds]
    seeds = [s.strip() for s in seeds if s and s.strip()]

    existing = store.load_all(config.content_dir)
    seen = {a.slug for a in existing}
    new: List[Article] = []

    for seed in seeds:
        if len(new) >= per_run:
            break
        ev(f"キーワード展開：「{seed}」")
        candidates = keywords.expand(seed, max(per_run * 4, 20), config)
        for kw in candidates:
            if len(new) >= per_run:
                break
            slug = generate.slugify(kw)
            if slug in seen:
                continue  # already written -> skip (saves an API call)
            ev(f"記事生成：{kw}")
            art = generate.generate(kw, config)
            if art.slug in seen:
                continue
            art.body_md = affiliate.inject(art.body_md, kw, config)
            store.save_article(art, config.content_dir)
            seen.add(art.slug)
            new.append(art)

    all_articles = store.load_all(config.content_dir)
    ev(f"サイト出力：{config.base_dir}/（全{len(all_articles)}記事）")
    render.render_site(all_articles, config)

    return Report(new_articles=new, total=len(all_articles), out_dir=config.base_dir)


def build(config: Config, *, on_event: Optional[Callable[[str], None]] = None) -> int:
    """Rebuild the static site from the content store, generating nothing."""
    articles = store.load_all(config.content_dir)
    if on_event:
        on_event(f"再ビルド：{len(articles)}記事 → {config.base_dir}/")
    render.render_site(articles, config)
    return len(articles)
