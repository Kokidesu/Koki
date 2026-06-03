"""雑学ナレーション台本の生成。"""
from __future__ import annotations

from dataclasses import dataclass, field

from . import llm


@dataclass
class Script:
    topic: str
    hook: str
    lines: list[str] = field(default_factory=list)
    cta: str = ""
    caption: str = ""
    hashtags: list[str] = field(default_factory=list)

    def narration(self) -> str:
        """TTSに渡す読み上げ全文。"""
        parts = [self.hook, *self.lines, self.cta]
        return "。\n".join(p.strip().rstrip("。") for p in parts if p and p.strip()) + "。"

    def to_dict(self) -> dict:
        return {
            "topic": self.topic,
            "hook": self.hook,
            "lines": self.lines,
            "cta": self.cta,
            "caption": self.caption,
            "hashtags": self.hashtags,
            "narration": self.narration(),
        }


_SYSTEM = (
    "あなたはTikTokで伸びる雑学ショートの構成作家です。"
    "30〜40秒・話し言葉・テンポ重視。最初の2秒で掴み、最後に軽い問いかけで締めます。"
    "難しい言葉は避け、断定しすぎず、事実として怪しい部分は作らないこと。"
)


def generate(topic: str, language: str = "ja") -> Script:
    prompt = (
        f"次の雑学を、TikTokショート用の日本語ナレーション台本にしてください: 「{topic}」\n\n"
        "次のJSONのみを返してください:\n"
        "{\n"
        '  "hook": "最初の2秒で言う掴み（1文）",\n'
        '  "lines": ["本編のナレーションを3〜5個の短文に分割", "..."],\n'
        '  "cta": "最後の一言（保存やコメントを促す軽い締め）",\n'
        '  "caption": "投稿キャプション（80字以内・絵文字少々OK）",\n'
        '  "hashtags": ["#雑学", "#豆知識", "..."]\n'
        "}\n"
        "条件: 1文は短く / 専門用語は噛み砕く / 数字は具体的に / 誇張や未確認情報は入れない。"
    )
    data = llm.complete_json(_SYSTEM, prompt, max_tokens=1200, temperature=0.85)
    return Script(
        topic=topic,
        hook=str(data.get("hook", "")).strip(),
        lines=[str(x).strip() for x in data.get("lines", []) if str(x).strip()],
        cta=str(data.get("cta", "")).strip(),
        caption=str(data.get("caption", "")).strip(),
        hashtags=[str(h).strip() for h in data.get("hashtags", []) if str(h).strip()],
    )
