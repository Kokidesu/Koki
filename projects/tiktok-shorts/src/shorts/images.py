"""AI画像生成（各セリフに合わせた背景画像）。

- build_prompts(): 台本の各区間に対応する英語の画像プロンプトをClaudeで作る
- generate()      : 画像生成APIで画像を作る（既定 OpenAI Images / 差し替え可）

字幕が読みやすいよう「下部は暗め・文字なし・縦構図」を指示する。
画像生成にはプロバイダのキーが必要（既定: OPENAI_API_KEY）。
"""
from __future__ import annotations

import base64
import os
from pathlib import Path

from . import llm

_SYS = (
    "You write concise, vivid prompts for an IMAGE generation model. "
    "These images are vertical (9:16) backgrounds for a short trivia video. "
    "Rules: cinematic, photorealistic or tasteful illustration; NO text, words, letters or captions in the image; "
    "keep the LOWER THIRD darker and simple so white subtitles stay readable; "
    "single clear subject; safe-for-work."
)


def build_prompts(scr) -> list[str]:
    segments = [s for s in [scr.hook, *scr.lines, scr.cta] if s and s.strip()]
    body = "\n".join(f"{i + 1}. {s}" for i, s in enumerate(segments))
    prompt = (
        f"Trivia topic (Japanese): {scr.topic}\n"
        f"Below are {len(segments)} narration lines (Japanese). For EACH line, in order, "
        "write ONE English image prompt (<= 25 words) for a background that visually fits that line.\n"
        f"Return ONLY a JSON array of {len(segments)} strings.\n\nLines:\n{body}"
    )
    try:
        data = llm.complete_json(_SYS, prompt, max_tokens=1200, temperature=0.7)
        if isinstance(data, dict):
            data = data.get("prompts") or next((v for v in data.values() if isinstance(v, list)), [])
        prompts = [str(x).strip() for x in data if str(x).strip()]
        if len(prompts) >= len(segments):
            return prompts[:len(segments)]
        # 足りなければ汎用で埋める
        prompts += [f"cinematic vertical background about {scr.topic}, no text, dark lower third"
                    ] * (len(segments) - len(prompts))
        return prompts
    except Exception as e:  # noqa: BLE001
        print(f"[images] プロンプト生成に失敗→汎用プロンプト: {e}")
        return [f"cinematic vertical background about {scr.topic}, no text, dark lower third, high detail"
                for _ in segments]


def _size_for(model: str) -> str:
    return "1024x1792" if model.startswith("dall-e-3") else "1024x1536"


def _openai_images(prompts: list[str], out_dir: Path, model: str) -> list[str]:
    import requests
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY が未設定です（.env を確認）")
    out = []
    for i, p in enumerate(prompts):
        r = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers={"Authorization": f"Bearer {key}"},
            json={"model": model, "prompt": p, "size": _size_for(model), "n": 1},
            timeout=180,
        )
        r.raise_for_status()
        d = r.json()["data"][0]
        path = out_dir / f"img_{i:02d}.png"
        if d.get("b64_json"):
            path.write_bytes(base64.b64decode(d["b64_json"]))
        else:
            path.write_bytes(requests.get(d["url"], timeout=180).content)
        out.append(str(path))
    return out


def generate(prompts: list[str], out_dir: str, provider: str | None = None,
             model: str | None = None) -> list[str]:
    provider = provider or os.environ.get("IMAGE_PROVIDER", "openai")
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    if provider == "openai":
        return _openai_images(prompts, Path(out_dir), model or "gpt-image-1")
    raise RuntimeError(f"未対応の画像プロバイダ: {provider}")
