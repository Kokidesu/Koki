"""単語境界 → 字幕(ASS) 生成。大きめ・中央下・縁取りのショート向けスタイル。"""
from __future__ import annotations

from pathlib import Path

_PUNCT = "。、！？!?…"


def _fmt_time(t: float) -> str:
    if t < 0:
        t = 0.0
    cs = int(round(t * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h:d}:{m:02d}:{s:02d}.{cs:02d}"


def _chunk(boundaries: list[dict], max_chars: int = 16) -> list[dict]:
    """単語境界を字幕1枚ぶんのまとまりにグループ化。"""
    chunks: list[dict] = []
    cur: list[dict] = []
    cur_len = 0
    for w in boundaries:
        txt = w["text"]
        cur.append(w)
        cur_len += len(txt)
        ends_sentence = txt and txt[-1] in _PUNCT
        if cur_len >= max_chars or ends_sentence:
            chunks.append({
                "text": "".join(x["text"] for x in cur).strip(),
                "start": cur[0]["start"],
                "end": cur[-1]["end"],
            })
            cur, cur_len = [], 0
    if cur:
        chunks.append({
            "text": "".join(x["text"] for x in cur).strip(),
            "start": cur[0]["start"],
            "end": cur[-1]["end"],
        })
    return [c for c in chunks if c["text"]]


def build_ass(boundaries: list[dict], out_path: str,
              resolution=(1080, 1920), font: str = "Noto Sans CJK JP",
              total_duration: float | None = None, max_chars: int = 16) -> str:
    w, h = resolution
    fontsize = int(w * 0.072)  # 解像度に対して相対サイズ

    if boundaries:
        chunks = _chunk(boundaries, max_chars=max_chars)
    elif total_duration:  # フォールバック: 境界が無ければ1枚で全画面表示
        chunks = [{"text": "", "start": 0.0, "end": total_duration}]
    else:
        chunks = []

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {w}
PlayResY: {h}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV
Style: Main,{font},{fontsize},&H00FFFFFF,&H00000000,&H64000000,1,1,{max(3, fontsize // 12)},2,2,80,80,{int(h * 0.18)}

[Events]
Format: Layer, Start, End, Style, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    for c in chunks:
        text = c["text"].replace("\n", " ").replace("{", "(").replace("}", ")")
        lines.append(
            f"Dialogue: 0,{_fmt_time(c['start'])},{_fmt_time(c['end'])},Main,,0,0,0,,{text}"
        )

    Path(out_path).write_text(header + "\n".join(lines) + "\n", encoding="utf-8")
    return out_path
