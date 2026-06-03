"""Command-line interface for koki-affiliate."""

from __future__ import annotations

import argparse
import os
import sys
from typing import List, Optional

from . import keywords, llm, pipeline
from .config import Config


def _build_config(args: argparse.Namespace) -> Config:
    cfg = Config.load(getattr(args, "config", None))
    if getattr(args, "out", None):
        cfg.base_dir = args.out
    if getattr(args, "amazon_tag", None):
        cfg.amazon_tag = args.amazon_tag
    if getattr(args, "site_url", None):
        cfg.site_url = args.site_url
    return cfg


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="affiliate",
        description="全自動アフィリエイト記事ジェネレーター（キーワード→生成→静的サイト）",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="記事を生成してサイトを出力する")
    r.add_argument("--seed", required=True, help="シードキーワード（例: ロボット掃除機）")
    r.add_argument("--count", type=int, default=3, help="生成する記事数（既定: 3）")
    r.add_argument("--out", help="出力ディレクトリ（既定: config の base_dir）")
    r.add_argument("--config", help="設定TOMLファイルのパス")
    r.add_argument("--amazon-tag", dest="amazon_tag", help="Amazonアソシエイトのタグ")
    r.add_argument("--site-url", dest="site_url", help="公開先のベースURL")

    k = sub.add_parser("keywords", help="キーワードだけ展開する")
    k.add_argument("--seed", required=True)
    k.add_argument("--count", type=int, default=10)
    k.add_argument("--config")

    args = parser.parse_args(argv)
    cfg = _build_config(args)

    if args.cmd == "keywords":
        for kw in keywords.expand(args.seed, args.count, cfg):
            print(kw)
        return 0

    if args.cmd == "run":
        mode = "Claude（本番生成）" if llm.have_llm() else "テンプレ（オフライン fallback）"
        print(f"🤖 生成モード: {mode}")
        report = pipeline.run(
            args.seed, args.count, cfg, on_event=lambda m: print("  • " + m)
        )
        index = os.path.join(cfg.base_dir, "index.html")
        print(f"\n✅ 完了: {len(report.articles)}記事を生成 → {index}")
        print(f"   ブラウザで開く: file://{os.path.abspath(index)}")
        if not llm.have_llm():
            print(
                "   ※ いまはテンプレ生成です。ANTHROPIC_API_KEY を設定すると"
                "Claudeが本物の記事を書きます。"
            )
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
