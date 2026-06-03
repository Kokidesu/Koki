"""字幕(ASS)生成。

- build_ass()       : TTSの単語境界からタイミングを作る（推奨）
- build_estimated() : 単語境界が無いTTS用。文字数で時間を比例配分する

style:
- "karaoke" : 読み上げに同期して1語ずつ色が乗る（CapCut風・既定）
- "plain"   : 区間ごとに表示するだけ

日本語は単語間スペースが無く libass の自動折返しが効かないため、
plainでは自前で改行(\\N)を入れる（数字や英単語の途中では割らない）。
karaokeは1行に収まる長さに分割する。
"""
from __future__ import annotations

import math
from pathlib import Path

_PUNCT = "。、！？!?…，,."
_FONT_RATIO = 0.064
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
    return max(6, int((w - 2 * _MARGIN) / _fontsize(w)))


def _rgb_to_ass(hex_color: str, default: str = "&H0000E1FF") -> str:
    """#RRGGBB → ASSの &H00BBGGRR。"""
    h = (hex_color or "").strip().lstrip("#")
    if len(h) != 6:
        return default
    return f"&H00{h[4:6]}{h[2:4]}{h[0:2]}".upper()


def _is_token_char(c: str) -> bool:
    return c.isascii() and c.isalnum()


def _break_at(text: str, target: int) -> int:
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


def _hardcap(pieces: list[str], cap: int) -> list[str]:
    """karaoke用: cap超の節をトークンを割らずに分割。"""
    out: list[str] = []
    for p in pieces:
        while len(p) > cap:
            idx = _break_at(p, cap)
            out.append(p[:idx])
            p = p[idx:]
        if p:
            out.append(p)
    return out


def _split_text(text: str, max_chars: int) -> list[str]:
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
    """単語境界を、テロップ1枚（words入り）にまとめる。"""
    chunks, cur, cur_len = [], [], 0

    def flush():
        if cur:
            chunks.append({"start": cur[0]["start"], "end": cur[-1]["end"],
                           "words": [dict(w) for w in cur]})

    for w in boundaries:
        cur.append(w)
        cur_len += len(w["text"])
        if cur_len >= max_chars or (w["text"] and w["text"][-1] in _PUNCT):
            flush()
            cur, cur_len = [], 0
    flush()
    return chunks


def _units_from_words(words: list[dict]) -> list[dict]:
    units = []
    for w in words:
        txt = w["text"].strip()
        if not txt:
            continue
        units.append({"text": txt, "dur": max(0.06, w["end"] - w["start"])})
    return units


def _units_from_text(text: str, duration: float) -> list[dict]:
    """1文字=1ユニットで均等割り（日本語のカラオケ塗りに自然）。"""
    chars = [c for c in text]
    n = len(chars) or 1
    per = duration / n
    return [{"text": c, "dur": per} for c in chars]


def _kara(units: list[dict]) -> str:
    parts = []
    for u in units:
        cs = max(1, int(round(u["dur"] * 100)))
        parts.append(f"{{\\kf{cs}}}{u['text']}")
    return "".join(parts)


def _ass_document(chunks: list[dict], resolution, font: str,
                  style: str = "karaoke", accent: str = "#FFE100") -> str:
    w, h = resolution
    fontsize = _fontsize(w)
    cap = _line_capacity(w)
    outline = max(4, fontsize // 9)
    shadow = max(1, fontsize // 24)
    accent_ass = _rgb_to_ass(accent)
    white = "&H00FFFFFF"

    if style == "karaoke":
        primary, secondary = accent_ass, white   # 未読=白 → 読了=accent に塗られる
    else:
        primary, secondary = white, white

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {w}
PlayResY: {h}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV
Style: Main,{font},{fontsize},{primary},{secondary},&H00101010,&H64000000,1,1,{outline},{shadow},2,{_MARGIN},{_MARGIN},{int(h * 0.20)}

[Events]
Format: Layer, Start, End, Style, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    for c in chunks:
        start, end = _fmt_time(c["start"]), _fmt_time(c["end"])
        if style == "karaoke":
            body = r"{\fad(90,50)}" + _kara(c["units"])
        else:
            text = "".join(u["text"] for u in c["units"]).replace("\n", " ")
            text = text.replace("{", "(").replace("}", ")")
            body = r"{\fad(90,50)}" + _wrap(text, cap)
        lines.append(f"Dialogue: 0,{start},{end},Main,0,0,0,,{body}")
    return header + "\n".join(lines) + "\n"


def build_ass(boundaries: list[dict], out_path: str, resolution=(1080, 1920),
              font: str = "Noto Sans CJK JP", max_chars: int | None = None,
              style: str = "karaoke", accent: str = "#FFE100") -> str:
    cap = max_chars or _line_capacity(resolution[0])
    chunks = _chunk_boundaries(boundaries, cap) if boundaries else []
    for c in chunks:
        c["units"] = _units_from_words(c["words"])
    Path(out_path).write_text(_ass_document(chunks, resolution, font, style, accent), encoding="utf-8")
    return out_path


def build_estimated(segments: list[str], total_duration: float, out_path: str,
                    resolution=(1080, 1920), font: str = "Noto Sans CJK JP",
                    max_chars: int | None = None,
                    style: str = "karaoke", accent: str = "#FFE100") -> str:
    cap = max_chars or _line_capacity(resolution[0])
    pieces: list[str] = []
    for s in segments:
        if s and s.strip():
            pieces.extend(_split_text(s, cap))
    if style == "karaoke":
        pieces = _hardcap(pieces, cap)  # 1行に収める
    total_chars = sum(len(p) for p in pieces) or 1
    chunks, t = [], 0.0
    for p in pieces:
        dur = total_duration * len(p) / total_chars
        chunks.append({"start": t, "end": t + dur, "units": _units_from_text(p, dur)})
        t += dur
    Path(out_path).write_text(_ass_document(chunks, resolution, font, style, accent), encoding="utf-8")
    return out_path
