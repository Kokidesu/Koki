"""コマンドライン: research / script / make / batch / run。"""
from __future__ import annotations

import argparse
import json

from . import pipeline, script, trends
from .config import load_config


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="shorts", description="雑学ショート動画 量産パイプライン")
    p.add_argument("--config", default="config.yaml", help="設定ファイル (既定: config.yaml)")
    sub = p.add_subparsers(dest="cmd", required=True)

    pr = sub.add_parser("research", help="トレンド調査（ネタ一覧を出力）")
    pr.add_argument("-n", type=int, default=10)

    ps = sub.add_parser("script", help="台本を1本だけ生成して表示")
    ps.add_argument("topic")

    pm = sub.add_parser("make", help="動画を1本作る")
    pm.add_argument("topic")
    pm.add_argument("--publish", default="off", choices=["off", "draft", "direct"],
                    help="投稿モード (既定: off)")

    pb = sub.add_parser("batch", help="まとめて生成（投稿しない）")
    pb.add_argument("-n", type=int, default=None)

    prun = sub.add_parser("run", help="調査→生成→投稿(設定に従う)を一気に")
    prun.add_argument("-n", type=int, default=None)
    prun.add_argument("--publish", default=None, choices=["off", "draft", "direct"],
                      help="設定を上書きする投稿モード")

    args = p.parse_args(argv)
    cfg = load_config(args.config)

    if args.cmd == "research":
        topics = trends.fetch_trending(cfg["niche"], args.n, cfg["language"])
        print(json.dumps(topics, ensure_ascii=False, indent=2))

    elif args.cmd == "script":
        scr = script.generate(args.topic, cfg["language"])
        print(json.dumps(scr.to_dict(), ensure_ascii=False, indent=2))

    elif args.cmd == "make":
        rec = pipeline.make_one(args.topic, cfg, 1, args.publish)
        print(json.dumps(rec, ensure_ascii=False, indent=2))

    elif args.cmd == "batch":
        pipeline.run(args.n, publish_mode="off", config_path=args.config)

    elif args.cmd == "run":
        pipeline.run(args.n, publish_mode=args.publish, config_path=args.config)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
