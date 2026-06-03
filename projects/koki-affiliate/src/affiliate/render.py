"""Render articles into a static site (index, posts, css, sitemap, robots)."""

from __future__ import annotations

import html
from datetime import date
from pathlib import Path
from typing import List

from .config import Config
from .generate import Article
from .markdown import to_html

STYLE_CSS = """\
:root { --fg:#1c2430; --muted:#5b6b7c; --bg:#f7f8fa; --card:#fff; --accent:#2563eb; --line:#e6e9ef; }
* { box-sizing: border-box; }
body { margin:0; font-family: system-ui,-apple-system,"Hiragino Kaku Gothic ProN","Noto Sans JP",sans-serif;
  color:var(--fg); background:var(--bg); line-height:1.8; }
a { color:var(--accent); }
.site-header { background:var(--card); border-bottom:1px solid var(--line); padding:16px 20px; }
.site-header .logo { font-weight:700; font-size:1.15rem; text-decoration:none; color:var(--fg); }
main { max-width:760px; margin:0 auto; padding:28px 20px 60px; }
h1 { font-size:1.7rem; line-height:1.35; margin:.2em 0 .6em; }
h2 { font-size:1.3rem; margin:1.8em 0 .6em; padding-bottom:.3em; border-bottom:2px solid var(--line); }
.meta,.breadcrumb { color:var(--muted); font-size:.86rem; }
.breadcrumb { margin-bottom:1.2em; }
table { width:100%; border-collapse:collapse; margin:1.2em 0; background:var(--card); }
th,td { border:1px solid var(--line); padding:10px 12px; text-align:left; }
th { background:#eef2f8; }
.lead { color:var(--muted); font-size:1.05rem; }
.cards { display:grid; gap:16px; grid-template-columns:1fr; }
@media(min-width:620px){ .cards{ grid-template-columns:1fr 1fr; } }
.card { display:block; background:var(--card); border:1px solid var(--line); border-radius:12px;
  padding:18px; text-decoration:none; color:inherit; transition:.15s; }
.card:hover { border-color:var(--accent); transform:translateY(-2px); }
.card h2 { font-size:1.05rem; border:0; margin:0 0 .4em; }
.card p { margin:0; color:var(--muted); font-size:.9rem; }
.cta { background:#fff8ec; border:1px solid #f1d9a8; border-radius:12px; padding:18px; margin:1.6em 0; }
.cta-label { font-size:.72rem; letter-spacing:.08em; color:#a9762a; margin:0 0 .4em; font-weight:700; }
.cta .btn { display:inline-block; margin:6px 8px 0 0; padding:11px 18px; border-radius:8px;
  text-decoration:none; font-weight:700; color:#fff; }
.btn.amazon { background:#ff9900; } .btn.rakuten { background:#bf0000; }
.related ul { padding-left:1.1em; }
.site-footer { border-top:1px solid var(--line); background:var(--card); color:var(--muted);
  font-size:.85rem; padding:24px 20px; }
.site-footer .disclosure { max-width:760px; margin:0 auto .6em; }
.site-footer p:last-child { max-width:760px; margin:0 auto; }
"""


def _esc(s: str) -> str:
    return html.escape(s, quote=True)


def _page(*, title: str, description: str, body_html: str, config: Config, canonical: str) -> str:
    year = date.today().year
    return f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_esc(title)}</title>
<meta name="description" content="{_esc(description)}">
<link rel="canonical" href="{_esc(canonical)}">
<meta property="og:title" content="{_esc(title)}">
<meta property="og:description" content="{_esc(description)}">
<meta property="og:type" content="website">
<meta name="generator" content="koki-affiliate">
<link rel="stylesheet" href="style.css">
</head>
<body>
<header class="site-header"><a class="logo" href="index.html">{_esc(config.site_title)}</a></header>
<main>
{body_html}
</main>
<footer class="site-footer">
<p class="disclosure">{_esc(config.disclosure)}</p>
<p>© {year} {_esc(config.site_title)}</p>
</footer>
</body>
</html>
"""


def _article_body(art: Article, others: List[Article]) -> str:
    related = "".join(
        f'<li><a href="{o.slug}.html">{_esc(o.title)}</a></li>'
        for o in others
        if o.slug != art.slug
    )
    related_block = (
        f'<section class="related"><h2>関連記事</h2><ul>{related}</ul></section>'
        if related
        else ""
    )
    return f"""<article>
<p class="breadcrumb"><a href="index.html">ホーム</a> › {_esc(art.title)}</p>
<h1>{_esc(art.title)}</h1>
<p class="meta">公開日: {art.date} ・ 想定キーワード: {_esc(art.keyword)}</p>
{to_html(art.body_md)}
{related_block}
</article>"""


def _index_body(articles: List[Article], config: Config) -> str:
    cards = "".join(
        f'<a class="card" href="{a.slug}.html"><h2>{_esc(a.title)}</h2>'
        f"<p>{_esc(a.description)}</p></a>"
        for a in articles
    )
    lead = f'<p class="lead">{_esc(config.tagline)}</p>' if config.tagline else ""
    return f'<h1>{_esc(config.site_title)}</h1>{lead}<div class="cards">{cards}</div>'


def render_site(articles: List[Article], config: Config) -> List[str]:
    """Write the full static site; returns the list of file paths written."""
    base = Path(config.base_dir)
    base.mkdir(parents=True, exist_ok=True)
    written: List[str] = []
    site = config.site_url.rstrip("/")

    def write(name: str, content: str) -> None:
        p = base / name
        p.write_text(content, encoding="utf-8")
        written.append(str(p))

    write("style.css", STYLE_CSS)

    for art in articles:
        page = _page(
            title=art.title,
            description=art.description,
            body_html=_article_body(art, articles),
            config=config,
            canonical=f"{site}/{art.slug}.html",
        )
        write(f"{art.slug}.html", page)

    index = _page(
        title=config.site_title,
        description=config.tagline or config.site_title,
        body_html=_index_body(articles, config),
        config=config,
        canonical=f"{site}/index.html",
    )
    write("index.html", index)

    locs = [f"{site}/index.html"] + [f"{site}/{a.slug}.html" for a in articles]
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join(f"<url><loc>{_esc(u)}</loc></url>" for u in locs)
        + "</urlset>\n"
    )
    write("sitemap.xml", sitemap)
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {site}/sitemap.xml\n")

    return written
