"""
run_daily.py — 1回の実行で「生成 → 投稿」をまとめて行う。
Generate N articles and post each to note in one run.

GitHub Actions から1日3回呼ばれる想定（1回1本 × 3回 = 1日3本）。
Called 3x/day by GitHub Actions (1 article each = 3/day) by default.
"""
from __future__ import annotations

from pathlib import Path
import traceback

import yaml

from generate import generate_one
from post_note import post_article

HERE = Path(__file__).parent


def main() -> None:
    cfg = yaml.safe_load((HERE / "config.yaml").read_text(encoding="utf-8"))

    if "ここにあなたのテーマ" in cfg.get("theme", ""):
        raise SystemExit("config.yaml の theme を実際のテーマに書き換えてください。")

    n = int(cfg.get("articles_per_run", 1))
    for i in range(n):
        print(f"=== article {i+1}/{n} ===")
        try:
            meta = generate_one(cfg)
            md = str(Path(meta["dir"]) / "article.md")
            post_article(
                md_path=md,
                tags=cfg.get("tags", []),
                publish=bool(cfg.get("publish")),
                thumbnail=meta.get("thumbnail"),
                headless=True,
            )
        except Exception:
            print(f"[error] article {i+1} failed:\n{traceback.format_exc()}")
            # 1本失敗しても残りは続行 / keep going on failure


if __name__ == "__main__":
    main()
