"""バッチ・オーケストレーション: 調査→台本→音声→字幕→動画→(投稿)。"""
from __future__ import annotations

import json
import re
from pathlib import Path

from . import publish_tiktok, script, subtitles, trends, tts, video
from .config import load_config


def _slug(topic: str, index: int) -> str:
    safe = re.sub(r'[\\/:*?"<>|\n\r\t]+', "", topic).strip().replace(" ", "_")
    return f"{index:02d}_{safe[:28]}"


def make_one(topic: str, cfg: dict, index: int = 1,
             publish_mode: str | None = None, token: str | None = None) -> dict:
    """1本ぶんを生成（必要なら投稿）して記録dictを返す。"""
    out = Path(cfg["out_dir"])
    out.mkdir(parents=True, exist_ok=True)
    base = out / _slug(topic, index)

    scr = script.generate(topic, cfg["language"])

    audio = f"{base}.mp3"
    boundaries = tts.synthesize(scr.narration(), audio, cfg["voice"], cfg.get("speech_rate", "+0%"))

    ass = f"{base}.ass"
    total = None
    if not boundaries:
        try:
            total = video.probe_duration(audio)
        except Exception:  # noqa: BLE001
            total = None
    subtitles.build_ass(boundaries, ass, tuple(cfg["resolution"]), total_duration=total)

    mp4 = f"{base}.mp4"
    video.assemble(audio, ass, mp4, tuple(cfg["resolution"]), cfg["fps"],
                   cfg["backgrounds_dir"], cfg["music_dir"], cfg["music_volume"])

    rec = {"topic": topic, "script": scr.to_dict(),
           "files": {"audio": audio, "subtitles": ass, "video": mp4}}

    mode = publish_mode if publish_mode is not None else cfg["publish"]["mode"]
    if mode and mode != "off":
        try:
            title = (scr.caption or topic)
            if scr.hashtags:
                title = f"{title} {' '.join(scr.hashtags)}".strip()
            rec["publish"] = publish_tiktok.publish(
                mp4, mode, title, cfg["publish"]["privacy"], token)
        except Exception as e:  # noqa: BLE001 — 投稿失敗でも生成物は残す
            rec["publish"] = {"error": str(e)}
    return rec


def run(n: int | None = None, publish_mode: str | None = None,
        config_path: str = "config.yaml") -> list[dict]:
    cfg = load_config(config_path)
    n = n or cfg["videos_per_run"]
    out = Path(cfg["out_dir"])
    out.mkdir(parents=True, exist_ok=True)

    topics = trends.fetch_trending(cfg["niche"], n, cfg["language"])
    manifest: list[dict] = []
    for i, t in enumerate(topics, 1):
        topic = t["topic"] if isinstance(t, dict) else str(t)
        print(f"[{i}/{len(topics)}] {topic}")
        try:
            rec = make_one(topic, cfg, i, publish_mode, None)
        except Exception as e:  # noqa: BLE001
            rec = {"topic": topic, "error": str(e)}
            print(f"   ! 失敗: {e}")
        manifest.append(rec)
        (out / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    ok = sum(1 for r in manifest if "error" not in r)
    print(f"完了: {ok}/{len(manifest)} 本 → {out}/ (manifest.json)")
    return manifest
