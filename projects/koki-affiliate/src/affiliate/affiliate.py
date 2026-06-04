"""Affiliate link building and CTA injection.

Links carry rel="nofollow sponsored" — both an affiliate-program requirement
and the correct signal to send Google for paid/affiliate links.
"""

from __future__ import annotations

from urllib.parse import quote_plus

from .config import Config


def amazon_search_url(keyword: str, tag: str) -> str:
    base = f"https://www.amazon.co.jp/s?k={quote_plus(keyword)}"
    return f"{base}&tag={tag}" if tag else base


def rakuten_url(keyword: str, template: str) -> str:
    return template.format(kw=quote_plus(keyword))


def cta_html(keyword: str, config: Config) -> str:
    """A self-contained HTML CTA block (every line starts with '<' so the
    Markdown renderer passes it through verbatim)."""
    az = amazon_search_url(keyword, config.amazon_tag)
    rk = rakuten_url(keyword, config.rakuten_search)
    return (
        '<div class="cta">\n'
        '<p class="cta-label">PR / 広告</p>\n'
        f'<p>「{keyword}」の最新価格・在庫をチェック：</p>\n'
        f'<a class="btn amazon" rel="nofollow sponsored noopener" target="_blank" href="{az}">Amazonで探す</a>\n'
        f'<a class="btn rakuten" rel="nofollow sponsored noopener" target="_blank" href="{rk}">楽天で探す</a>\n'
        "</div>"
    )


def inject(body_md: str, keyword: str, config: Config) -> str:
    """Replace the {AFFILIATE_CTA} marker with a real CTA block."""
    cta = cta_html(keyword, config)
    return body_md.replace("{AFFILIATE_CTA}", f"\n\n{cta}\n\n")
