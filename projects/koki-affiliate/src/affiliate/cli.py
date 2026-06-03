"""Command-line interface for koki-affiliate."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import List, Optional

from . import keywords, llm, pipeline
from .config import Config


def _build_config(args: argparse.Namespace) -> Config:
    cfg = Config.load(getattr(args, "config", None))
    if getattr(args, "out", None):
        cfg.base_dir = args.out
    if getattr(args, "content", None):
        cfg.content_dir = args.content
    if getattr(args, "amazon_tag", None):
        cfg.amazon_tag = args.amazon_tag
    if getattr(args, "site_url", None):
        cfg.site_url = args.site_url
    return cfg


def _read_seeds(path: str) -> List[str]:
    out: List[str] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            out.append(line)
    return out


def _collect_seeds(args: argparse.Namespace) -> List[str]:
    seeds: List[str] = []
    if getattr(args, "seeds_file", None):
        seeds += _read_seeds(args.seeds_file)
    if getattr(args, "seed", None):
        seeds += list(args.seed)
    return seeds


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="affiliate",
        description="全自動アフィリエイト記事ジェネレーター（キーワード→生成→静的サイト）",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="新規記事を生成して保存し、サイトを再ビルドする")
    r.add_argument("--seed", nargs="+", help="シードキーワード（複数可）")
    r.add_argument("--seeds-file", dest="seeds_file", help="1行1シードのファイル")
    r.add_argument("--count", type=int, default=3, help="1回で増やす記事数（既定: 3）")
    r.add_argument("--out", help="サイト出力先（既定: config の base_dir）")
    r.add_argument("--content", help="記事データの保存先（既定: config の content_dir）")
    r.add_argument("--config", help="設定TOMLファイルのパス")
    r.add_argument("--amazon-tag", dest="amazon_tag", help="Amazonアソシエイトのタグ")
    r.add_argument("--site-url", dest="site_url", help="公開先のベースURL")

    b = sub.add_parser("build", help="保存済み記事からサイトだけ再ビルドする")
    b.add_argument("--out")
    b.add_argument("--content")
    b.add_argument("--config")
    b.add_argument("--site-url", dest="site_url")
    b.add_argument("--amazon-tag", dest="amazon_tag")

    k = sub.add_parser("keywords", help="キーワードだけ展開する")
    k.add_argument("--seed", nargs="+", required=True)
    k.add_argument("--count", type=int, default=10)
    k.add_argument("--config")

    args = parser.parse_args(argv)
    cfg = _build_config(args)

    if args.cmd == "keywords":
        for seed in args.seed:
            for kw in keywords.expand(seed, args.count, cfg):
                print(kw)
        return 0

    if args.cmd == "build":
        n = pipeline.build(cfg, on_event=lambda m: print("  • " + m))
        index = os.path.join(cfg.base_dir, "index.html")
        print(f"✅ 再ビルド完了: {n}記事 → {index}")
        return 0

    if args.cmd == "run":
        seeds = _collect_seeds(args)
        if not seeds:
            parser.error("--seed か --seeds-file を指定してください")
        mode = "Claude（本番生成）" if llm.have_llm() else "テンプレ（オフライン fallback）"
        print(f"🤖 生成モード: {mode}")
        report = pipeline.run(
            seeds, args.count, cfg, on_event=lambda m: print("  • " + m)
        )
        index = os.path.join(cfg.base_dir, "index.html")
        print(
            f"\n✅ 完了: 新規{len(report.new_articles)}記事 / 累計{report.total}記事"
            f" → {index}"
        )
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
