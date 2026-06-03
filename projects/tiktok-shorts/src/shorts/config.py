"""設定の読み込み（config.yaml をデフォルトにマージ）。"""
from __future__ import annotations

import copy
from pathlib import Path

DEFAULTS = {
    "niche": "雑学・豆知識",
    "language": "ja",
    "voice": "ja-JP-NanamiNeural",
    "speech_rate": "+8%",
    "videos_per_run": 10,
    "resolution": [1080, 1920],
    "fps": 30,
    "font": "Noto Sans CJK JP",     # 字幕フォント（システムにあるCJKフォント名）
    "fonts_dir": "assets/fonts",    # ここに .ttf/.otf を置けばそれも使われる
    "caption_style": "karaoke",     # karaoke(読み上げ同期で色が乗る) | plain
    "accent_color": "#FFE100",      # カラオケ字幕のハイライト色
    "backgrounds_dir": "assets/backgrounds",
    "music_dir": "assets/music",
    "music_volume": 0.12,
    "publish": {"mode": "draft", "privacy": "SELF_ONLY"},
    "out_dir": "out",
}


def _deep_merge(base: dict, override: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_config(path: str = "config.yaml") -> dict:
    cfg = copy.deepcopy(DEFAULTS)
    p = Path(path)
    if p.exists():
        import yaml  # lazy import so the package loads without PyYAML

        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        cfg = _deep_merge(cfg, data)
    return cfg
