"""字幕(ASS)生成。大きめ・中央下・縁取りのショート向けスタイル。

- build_ass()       : TTSの単語境界（推奨）からタイミングを作る
- build_estimated() : 単語境界が無いTTS用。文字数で時間を比例配分する

日本語は単語間スペースが無く libass の自動折返しが効かないため、
画面幅に収まるよう自前で改行(\\N)を入れる（数字や英単語の途中では割らない）。
"""
from __future__ import annotations

import math
from pathlib import Path

_PUNCT = "。、！？!?…，,."
_FONT_RATIO = 0.062
_MARGIN = 70


def _fmt_time(t: float) -> str:
    if t < 0:
        t = 0.0
    cs = int(round(t * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h:d}:{m:02d}:{s:02d}.{cs:02d}"


def _fontsize(w: int) -> int:
    return int(w * _FONT_RATIO)


def _line_capacity(w: int) -> int:
    """1行に収まる全角文字数の目安。"""
    return max(6, int((w - 2 * _MARGIN) / _fontsize(w)))


def _is_token_char(c: str) -> bool:
    """半角英数（"40" や "OK" など、途中で割りたくない文字）か。"""
    return c.isascii() and c.isalnum()


def _break_at(text: str, target: int) -> int:
    """target付近で、半角英数トークンの途中にならない改行位置を探す。"""
    n = len(text)
    for delta in range(n):
        for idx in (target - delta, target + delta):
            if 1 <= idx < n and not (_is_token_char(text[idx - 1]) and _is_token_char(text[idx])):
                return idx
    return target


def _wrap(text: str, cap: int) -> str:
    if len(text) <= cap:
        return text
    if len(text) <= 2 * cap:
        idx = _break_at(text, math.ceil(len(text) / 2))
        return text[:idx] + r"\N" + text[idx:]
    return r"\N".join(text[i:i + cap] for i in range(0, len(text), cap))


def _split_text(text: str, max_chars: int) -> list[str]:
    """句読点で区切り、短い節は max_chars まで結合（語の途中では切らない）。"""
    raw, cur = [], ""
    for ch in text:
        cur += ch
        if ch in _PUNCT:
            raw.append(cur)
            cur = ""
    if cur:
        raw.append(cur)
    cleaned = [p.strip().strip("".join(_PUNCT) + " ") for p in raw]
    cleaned = [c for c in cleaned if c]
    merged: list[str] = []
    for c in cleaned:
        if merged and len(merged[-1]) + len(c) <= max_chars:
            merged[-1] += c
        else:
            merged.append(c)
    return merged


def _chunk_boundaries(boundaries: list[dict], max_chars: int) -> list[dict]:
    chunks, cur, cur_len = [], [], 0
    for w in boundaries:
        cur.append(w)
        cur_len += len(w["text"])
        if cur_len >= max_chars or (w["text"] and w["text"][-1] in _PUNCT):
            chunks.append({"text": "".join(x["text"] for x in cur).strip(),
                           "start": cur[0]["start"], "end": cur[-1]["end"]})
            cur, cur_len = [], 0
    if cur:
        chunks.append({"text": "".join(x["text"] for x in cur).strip(),
                       "start": cur[0]["start"], "end": cur[-1]["end"]})
    return [c for c in chunks if c["text"]]


def _ass_document(chunks: list[dict], resolution, font: str) -> str:
    w, h = resolution
    fontsize = _fontsize(w)
    cap = _line_capacity(w)
    outline = max(3, fontsize // 12)
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {w}
PlayResY: {h}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV
Style: Main,{font},{fontsize},&H00FFFFFF,&H00000000,&H64000000,1,1,{outline},2,2,{_MARGIN},{_MARGIN},{int(h * 0.18)}

[Events]
Format: Layer, Start, End, Style, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    for c in chunks:
        text = c["text"].replace("\n", " ").replace("{", "(").replace("}", ")")
        text = _wrap(text, cap)
        lines.append(f"Dialogue: 0,{_fmt_time(c['start'])},{_fmt_time(c['end'])},Main,0,0,0,,{text}")
    return header + "\n".join(lines) + "\n"


def build_ass(boundaries: list[dict], out_path: str, resolution=(1080, 1920),
              font: str = "Noto Sans CJK JP", max_chars: int | None = None) -> str:
    cap = max_chars or _line_capacity(resolution[0])
    chunks = _chunk_boundaries(boundaries, cap) if boundaries else []
    Path(out_path).write_text(_ass_document(chunks, resolution, font), encoding="utf-8")
    return out_path


def build_estimated(segments: list[str], total_duration: float, out_path: str,
                    resolution=(1080, 1920), font: str = "Noto Sans CJK JP",
                    max_chars: int | None = None) -> str:
    """単語境界が無い場合: 文を割って、文字数に比例した時間で並べる。"""
    cap = max_chars or _line_capacity(resolution[0])
    pieces: list[str] = []
    for s in segments:
        if s and s.strip():
            pieces.extend(_split_text(s, cap))
    total_chars = sum(len(p) for p in pieces) or 1
    chunks, t = [], 0.0
    for p in pieces:
        dur = total_duration * len(p) / total_chars
        chunks.append({"text": p, "start": t, "end": t + dur})
        t += dur
    Path(out_path).write_text(_ass_document(chunks, resolution, font), encoding="utf-8")
    return out_path
