"""
generate.py — Gemini で note 記事（長文）とサムネ画像を生成する。
Generate a long-form note article + thumbnail image using Google Gemini.

出力 / output:
  output/<YYYY-MM-DD>/<slug>/
      article.md      … タイトル＋本文(Markdown)
      meta.json       … title / tags / chars など
      thumbnail.png   … サムネ画像（thumbnail: true のとき）
"""
from __future__ import annotations

import json
import os
import re
import datetime as dt
from pathlib import Path

from google import genai
from google.genai import types

HERE = Path(__file__).parent


def _client() -> genai.Client:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise SystemExit(
            "GEMINI_API_KEY が未設定です。Google AI Studio で取得して環境変数に入れてください。\n"
            "GEMINI_API_KEY is not set. Get one at https://aistudio.google.com/apikey"
        )
    return genai.Client(api_key=key)


def _gen_text(client: genai.Client, model: str, prompt: str) -> str:
    resp = client.models.generate_content(model=model, contents=prompt)
    return (resp.text or "").strip()


def _outline(client: genai.Client, cfg: dict) -> dict:
    """タイトルと見出し一覧をJSONで作る。"""
    prompt = f"""あなたは note のプロ編集者です。テーマ「{cfg['theme']}」で、
読者の役に立つ長文記事の構成案を作ってください。スタイル: {cfg.get('style','')}

次のJSONだけを返してください（前後の説明やコードフェンス不要）:
{{"title": "30文字前後の魅力的なタイトル",
  "sections": ["見出し1","見出し2","見出し3","見出し4","見出し5","見出し6","見出し7","見出し8"]}}
本文合計で約{cfg['target_chars']}文字になる想定で、見出しは8〜12個。"""
    raw = _gen_text(client, cfg["text_model"], prompt)
    raw = re.sub(r"^```[a-zA-Z]*|```$", "", raw.strip()).strip()
    try:
        data = json.loads(raw)
        assert data.get("title") and data.get("sections")
        return data
    except Exception:
        # フォールバック / fallback
        return {"title": cfg["theme"], "sections": [f"{cfg['theme']}について{i}" for i in range(1, 9)]}


def _write_sections(client: genai.Client, cfg: dict, outline: dict) -> str:
    """各見出しを順に執筆し、目標文字数に達するまで積み上げる。"""
    title = outline["title"]
    sections = outline["sections"]
    target = int(cfg["target_chars"])
    per = max(800, target // max(1, len(sections)))
    body_parts: list[str] = []
    total = 0
    for i, heading in enumerate(sections, 1):
        context = "\n".join(f"- {s}" for s in sections)
        prompt = f"""記事タイトル: 「{title}」
テーマ: {cfg['theme']}
全体の見出し構成:
{context}

いまから「{heading}」の節を約{per}文字で執筆してください。
- 見出し行は「## {heading}」で始める
- 具体例・手順・体験談を入れて読み応えを出す
- 箇条書きや小見出しも適宜使ってよい
- 前置きや「承知しました」等のメタ発言は禁止。本文だけ返す
スタイル: {cfg.get('style','')}"""
        part = _gen_text(client, cfg["text_model"], prompt)
        if not part.lstrip().startswith("#"):
            part = f"## {heading}\n\n{part}"
        body_parts.append(part)
        total += len(part)
        if total >= target:
            break
    body = "\n\n".join(body_parts)
    # 目標に届かない場合は1回だけ加筆 / one top-up pass if short
    if len(body) < target * 0.8:
        more = _gen_text(
            client, cfg["text_model"],
            f"次の記事に、まとめ・実践チェックリスト・よくある質問(FAQ)を約{target-len(body)}文字で追記してください。"
            f"本文だけ返す。\n\n---\n{body[-3000:]}",
        )
        body += "\n\n" + more
    return f"# {title}\n\n{body}\n"


def _slug(title: str) -> str:
    s = re.sub(r"\s+", "-", title.strip())
    s = re.sub(r"[^0-9A-Za-zぁ-んァ-ヶ一-龯ー-]", "", s)
    return (s or "note")[:40]


def _thumbnail(client: genai.Client, cfg: dict, title: str, out: Path) -> Path | None:
    if not cfg.get("thumbnail"):
        return None
    prompt = (f"note記事のアイキャッチ画像。テーマ「{cfg['theme']}」、タイトル「{title}」。"
              "文字は入れない。清潔感のあるモダンなイラスト/写真調。16:9。")
    try:
        res = client.models.generate_images(
            model=cfg["image_model"],
            prompt=prompt,
            config=types.GenerateImagesConfig(number_of_images=1, aspect_ratio="16:9"),
        )
        img = res.generated_images[0].image
        data = getattr(img, "image_bytes", None) or img.read()  # SDK差異の保険
        p = out / "thumbnail.png"
        p.write_bytes(data)
        return p
    except Exception as e:  # 画像生成は失敗しても記事は出す
        print(f"[warn] thumbnail generation failed: {e}")
        return None


def generate_one(cfg: dict) -> dict:
    """記事を1本生成してディレクトリに保存し、メタ情報を返す。"""
    client = _client()
    outline = _outline(client, cfg)
    body_md = _write_sections(client, cfg, outline)
    title = outline["title"]

    day = dt.date.today().isoformat()
    out = HERE / "output" / day / _slug(title)
    out.mkdir(parents=True, exist_ok=True)
    (out / "article.md").write_text(body_md, encoding="utf-8")

    thumb = _thumbnail(client, cfg, title, out)
    meta = {
        "title": title,
        "tags": cfg.get("tags", []),
        "chars": len(body_md),
        "publish": bool(cfg.get("publish")),
        "thumbnail": str(thumb) if thumb else None,
        "dir": str(out),
        "created_at": dt.datetime.now().isoformat(timespec="seconds"),
    }
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[ok] generated: {title} ({len(body_md)}字) -> {out}")
    return meta


if __name__ == "__main__":
    import yaml
    cfg = yaml.safe_load((HERE / "config.yaml").read_text(encoding="utf-8"))
    generate_one(cfg)
