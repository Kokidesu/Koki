"""Configuration loading (TOML, stdlib only)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None  # type: ignore


@dataclass
class Config:
    # --- site ---
    site_title: str = "おすすめ研究所"
    site_url: str = "https://example.com"
    base_dir: str = "out"
    content_dir: str = "content"
    tagline: str = ""
    disclosure: str = (
        "当サイトはアフィリエイトプログラムを利用しています。"
        "記事内のリンクから商品が購入されると、当サイトが収益を得る場合があります。"
    )
    # --- affiliate ---
    amazon_tag: str = ""
    rakuten_search: str = "https://search.rakuten.co.jp/search/mall/{kw}/"
    # --- generation ---
    model: str = "claude-sonnet-4-6"
    words: int = 1200
    tone: str = "親しみやすく、初心者にもわかりやすい"

    @classmethod
    def load(cls, path: str | None) -> "Config":
        """Load config from a TOML file, falling back to defaults."""
        if not path:
            return cls()
        p = Path(path)
        if not p.exists() or tomllib is None:
            return cls()
        data = tomllib.loads(p.read_text(encoding="utf-8"))
        aff = data.get("affiliate", {})
        gen = data.get("generation", {})
        return cls(
            site_title=data.get("site_title", cls.site_title),
            site_url=data.get("site_url", cls.site_url),
            base_dir=data.get("base_dir", cls.base_dir),
            content_dir=data.get("content_dir", cls.content_dir),
            tagline=data.get("tagline", cls.tagline),
            disclosure=data.get("disclosure", cls.disclosure),
            amazon_tag=aff.get("amazon_tag", cls.amazon_tag),
            rakuten_search=aff.get("rakuten_search", cls.rakuten_search),
            model=gen.get("model", cls.model),
            words=gen.get("words", cls.words),
            tone=gen.get("tone", cls.tone),
        )
