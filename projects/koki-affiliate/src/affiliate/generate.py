"""Article generation: a structured post per keyword (Claude or template)."""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import date

from . import llm
from .config import Config

# Placeholder that marks where the affiliate CTA should be injected.
CTA_MARK = "{AFFILIATE_CTA}"


@dataclass
class Article:
    keyword: str
    title: str
    description: str
    slug: str
    body_md: str
    date: str
    generator: str  # "claude" | "template"


def slugify(text: str, fallback: str = "article") -> str:
    """URL slug that keeps Japanese characters (good for SEO) and drops
    symbols. Spaces become hyphens; ASCII is lowercased."""
    t = unicodedata.normalize("NFKC", text).strip()
    t = re.sub(r"\s+", "-", t)
    t = re.sub(r"[^\w\-]", "", t)  # \w keeps JP letters + alnum + underscore
    t = t.strip("-").lower()
    return t or fallback


def generate(keyword: str, config: Config) -> Article:
    """Generate one article for a keyword (Claude when available)."""
    if llm.have_llm():
        try:
            return _generate_llm(keyword, config)
        except Exception:
            pass
    return _generate_template(keyword, config)


def _generate_llm(keyword: str, config: Config) -> Article:
    system = (
        "あなたは経験豊富な日本語SEOライター兼アフィリエイターです。"
        "読者の検索意図を満たす、独自性と具体性のある記事を書きます。"
        "誇大広告や、事実に基づかない体験談・効果効能は書きません。"
    )
    prompt = f"""次のキーワードで日本語のブログ記事を書いてください。
キーワード: {keyword}
トーン: {config.tone}
目安文字数: {config.words}字

出力は必ず次のJSONのみ（前後に説明文やコードフェンスを付けないこと）:
{{"title": "32文字程度の魅力的なタイトル",
  "description": "120文字程度のメタディスクリプション",
  "body_markdown": "Markdown本文。h2(##)から始め、導入→選び方→比較→FAQ→まとめの構成。比較には表(| 列 | 列 |)を使う。商品を勧めたい箇所に必ず一度だけ {CTA_MARK} という文字列を置く。"}}"""
    text = llm.complete(
        prompt, system=system, model=config.model, max_tokens=max(2000, config.words * 3)
    )
    data = _parse_json(text)
    title = (data.get("title") or keyword).strip()
    desc = (data.get("description") or "").strip()
    body = (data.get("body_markdown") or text).strip()
    if CTA_MARK not in body:
        body += f"\n\n{CTA_MARK}\n"
    return Article(
        keyword=keyword,
        title=title,
        description=desc,
        slug=slugify(keyword),
        body_md=body,
        date=date.today().isoformat(),
        generator="claude",
    )


def _parse_json(text: str) -> dict:
    t = text.strip()
    t = re.sub(r"^```(?:json)?", "", t).strip()
    t = re.sub(r"```$", "", t).strip()
    m = re.search(r"\{.*\}", t, re.S)
    if m:
        t = m.group(0)
    try:
        return json.loads(t)
    except Exception:
        return {}


def _generate_template(keyword: str, config: Config) -> Article:
    year = date.today().year
    title = f"【{year}年最新】{keyword}の選び方とおすすめを徹底解説"
    description = (
        f"{keyword}について、選び方の3つのポイントとタイプ別の比較、"
        f"よくある質問をまとめました。失敗しない選び方をわかりやすく解説します。"
    )
    body = f"""## {keyword}を選ぶ前に知っておきたいこと

{keyword}を検討している方に向けて、選び方のポイントとおすすめの探し方をまとめました。
種類や価格帯が幅広いため、最初に「自分の目的」を整理しておくと失敗しにくくなります。

## 失敗しない選び方の3つのポイント

- **目的に合っているか** — 何のために使うかをはっきりさせると候補が絞れます。
- **予算とのバランス** — 高ければ良いとは限らず、価格と機能の釣り合いが大切です。
- **口コミ・評判** — 実際の利用者の声は、スペック表に出ない使い勝手を教えてくれます。

## タイプ別の比較

| タイプ | 特徴 | こんな人におすすめ |
| --- | --- | --- |
| エントリー | 価格が手頃で扱いやすい | はじめて購入する方 |
| スタンダード | 機能と価格のバランスが良い | 迷ったらこれ |
| ハイエンド | 高機能・高性能 | こだわって選びたい方 |

## よくある質問

**Q. 初心者でも使えますか？** — はい。まずはエントリーモデルから始めれば十分です。

**Q. どこで買うのがお得ですか？** — 時期やセールによって変わるため、複数のショップで価格を比べるのがおすすめです。

## まとめ

{keyword}は「目的」と「予算」に合わせて選ぶのが、失敗しないいちばんのコツです。
気になった方は、下記から最新の価格や在庫をチェックしてみてください。

{CTA_MARK}
"""
    return Article(
        keyword=keyword,
        title=title,
        description=description,
        slug=slugify(keyword),
        body_md=body,
        date=date.today().isoformat(),
        generator="template",
    )
