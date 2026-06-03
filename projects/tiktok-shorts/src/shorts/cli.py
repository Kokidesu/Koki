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

    prn = sub.add_parser("render", help="保存済みの台本JSONから動画を作る")
    prn.add_argument("path", help="台本JSON（例: samples/scripts/01_banana.json）")
    prn.add_argument("--publish", default="off", choices=["off", "draft", "direct"])

    sub.add_parser("doctor", help="環境チェック（ffmpeg/依存/連携状態）")

    pa = sub.add_parser("auth", help="TikTokアカウント連携(OAuth)・トークン管理")
    pa.add_argument("action", nargs="?", default="status",
                    choices=["url", "login", "status", "refresh"],
                    help="url=連携URL表示 / login=コード投入 / status=状態 / refresh=更新")
    pa.add_argument("code", nargs="?", help="login時: リダイレクトURL または code")

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

    elif args.cmd == "render":
        with open(args.path, encoding="utf-8") as f:
            data = json.load(f)
        scr = script.Script.from_dict(data)
        rec = pipeline.make_from_script(scr, cfg, 1, args.publish)
        print(json.dumps(rec, ensure_ascii=False, indent=2))

    elif args.cmd == "doctor":
        import os
        from . import auth_tiktok as at, video
        print("== 環境チェック ==")
        for b in ("ffmpeg", "ffprobe"):
            try:
                print(f"{b:8}: OK ({video._require(b)})")
            except Exception as e:  # noqa: BLE001
                print(f"{b:8}: NG — {e}")
        for mod in ("edge_tts", "requests", "yaml", "anthropic"):
            try:
                __import__(mod)
                print(f"{mod:8}: OK")
            except Exception:  # noqa: BLE001
                print(f"{mod:8}: 未インストール（pip install -r requirements.txt）")
        print("ANTHROPIC_API_KEY:", "設定済み" if os.environ.get("ANTHROPIC_API_KEY") else "未設定")
        print(at.status_text())

    elif args.cmd == "auth":
        from . import auth_tiktok as at
        try:
            if args.action == "url":
                url = at.authorize_url()
                print("① 下のURLをブラウザで開き、対象アカウントで承認してください:\n")
                print(url)
                print("\n② 承認後に飛ぶリダイレクト先URL（?code=... 付き）を丸ごとコピーし:\n"
                      '   PYTHONPATH=src python -m shorts auth login "<貼り付け>"')
            elif args.action == "login":
                if not args.code:
                    print('使い方: shorts auth login "<リダイレクトURL または code>"')
                    return 2
                t = at.exchange_code(at.parse_code(args.code))
                print(f"連携成功 ✅ open_id={t.get('open_id', '?')} scope={t.get('scope', '?')}")
            elif args.action == "refresh":
                t = at.refresh()
                print(f"トークン更新 ✅ 有効期限(秒)={t.get('expires_in')}")
            else:  # status
                print(at.status_text())
        except Exception as e:  # noqa: BLE001 — 設定不足などを分かりやすく表示
            print(f"エラー: {e}")
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
