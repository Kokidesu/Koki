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


def _produce(scr: script.Script, cfg: dict, index: int = 1,
             publish_mode: str | None = None, token: str | None = None) -> dict:
    """台本(Script)→音声→字幕→動画→(投稿) の本体。"""
    out = Path(cfg["out_dir"])
    out.mkdir(parents=True, exist_ok=True)
    base = out / _slug(scr.topic or "video", index)
    res = tuple(cfg["resolution"])

    audio = f"{base}.mp3"
    boundaries = tts.synthesize(scr.narration(), audio, cfg["voice"], cfg.get("speech_rate", "+0%"))

    ass = f"{base}.ass"
    font = cfg.get("font", "Noto Sans CJK JP")
    style = cfg.get("caption_style", "karaoke")
    accent = cfg.get("accent_color", "#FFE100")
    if boundaries:
        subtitles.build_ass(boundaries, ass, res, font=font, style=style, accent=accent)
    else:  # 単語境界を返さないTTS用に、文字数で時間配分
        dur = video.probe_duration(audio)
        subtitles.build_estimated([scr.hook, *scr.lines, scr.cta], dur, ass, res,
                                  font=font, style=style, accent=accent)

    mp4 = f"{base}.mp4"
    video.assemble(audio, ass, mp4, res, cfg["fps"],
                   cfg["backgrounds_dir"], cfg["music_dir"], cfg["music_volume"],
                   fonts_dir=cfg.get("fonts_dir"))

    rec = {"topic": scr.topic, "script": scr.to_dict(),
           "files": {"audio": audio, "subtitles": ass, "video": mp4}}

    mode = publish_mode if publish_mode is not None else cfg["publish"]["mode"]
    if mode and mode != "off":
        try:
            title = scr.caption or scr.topic
            if scr.hashtags:
                title = f"{title} {' '.join(scr.hashtags)}".strip()
            rec["publish"] = publish_tiktok.publish(
                mp4, mode, title, cfg["publish"]["privacy"], token)
        except Exception as e:  # noqa: BLE001 — 投稿失敗でも生成物は残す
            rec["publish"] = {"error": str(e)}
    return rec


def make_one(topic: str, cfg: dict, index: int = 1,
             publish_mode: str | None = None, token: str | None = None) -> dict:
    """トピック文字列から台本を生成して1本作る。"""
    scr = script.generate(topic, cfg["language"])
    return _produce(scr, cfg, index, publish_mode, token)


def make_from_script(scr: script.Script, cfg: dict, index: int = 1,
                     publish_mode: str | None = None, token: str | None = None) -> dict:
    """保存済みの台本(JSON)から1本作る（手書き台本の利用に便利）。"""
    return _produce(scr, cfg, index, publish_mode, token)


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
