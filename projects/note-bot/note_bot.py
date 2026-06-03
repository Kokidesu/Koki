"""
note_bot.py — Gemini で記事＋サムネを生成し、note へ自動投稿する（ローカル実行版・1ファイル）。

設計（シンプル最優先）:
- クラウド/Secret/Cookie 不要。あなたのMacで動かすだけ。
- 投稿は専用Chromeプロファイル（このフォルダ内 .note-profile/）を使う。
  → 初回だけ開いたChromeでnoteにログインすれば、以降はログイン状態が保存され自動。
- once（1回）/ loop（PC起動中ずっと・間隔＆1日上限つき）。

使い方:
  pip install -r requirements.txt
  python -m playwright install chromium
  export GEMINI_API_KEY=...        # あなたのGeminiキー
  python note_bot.py               # config.yaml に従って実行
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import time
import traceback
from pathlib import Path

import yaml
from google import genai
from google.genai import types
from playwright.sync_api import sync_playwright, Page, TimeoutError as PWTimeout

HERE = Path(__file__).parent
PROFILE = HERE / ".note-profile"          # ログイン状態を保存する専用プロファイル
OUT = HERE / "output"
STATE = OUT / "state.json"
EDITOR_URL = "https://note.com/notes/new"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def load_cfg() -> dict:
    return yaml.safe_load((HERE / "config.yaml").read_text(encoding="utf-8"))


def gem() -> genai.Client:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise SystemExit("GEMINI_API_KEY が未設定です。 export GEMINI_API_KEY=... を実行してください。")
    return genai.Client(api_key=key)


# ===================== 生成（Gemini） =====================
def _text(c, model, prompt) -> str:
    return (c.models.generate_content(model=model, contents=prompt).text or "").strip()


def _slug(t: str) -> str:
    s = re.sub(r"\s+", "-", t.strip())
    s = re.sub(r"[^0-9A-Za-zぁ-んァ-ヶ一-龯ー-]", "", s)
    return (s or "note")[:40]


def detect_theme(c, conf, page: Page) -> str:
    """ログイン済みページで自分のアカウントを読み、テーマを推定。"""
    urlname = conf["account_url"].rstrip("/").split("/")[-1]
    info = page.evaluate(
        """async (u) => {
            const out = {bio:'', titles:[]};
            try { const r=await fetch(`/api/v2/creators/${u}`); if(r.ok){const d=(await r.json()).data||{};
                  out.bio=[d.nickname,d.profile,d.description].filter(Boolean).join('\\n');} } catch(e){}
            try { const r=await fetch(`/api/v2/creators/${u}/contents?kind=note&page=1`); if(r.ok){
                  const d=(await r.json()).data||{}; out.titles=(d.contents||[]).map(x=>x.name).filter(Boolean);} } catch(e){}
            return out;
        }""", urlname)
    if not info.get("titles") and not info.get("bio"):
        raise SystemExit("アカウントを読めませんでした。config.yaml の theme を手動で指定してください。")
    theme = _text(c, conf.get("text_model", "gemini-2.5-pro"),
                  "次のnoteのプロフと記事タイトルから、今後書くべき記事の『テーマ』を日本語1文で。前置き不要、テーマだけ。\n\n"
                  f"プロフ:\n{info['bio']}\n\nタイトル:\n- " + "\n- ".join(info["titles"]))
    theme = theme.strip().strip("「」\"' 　")
    print(f"[theme] アカLから推定: {theme}")
    return theme


def generate(c, conf) -> dict:
    theme = conf["theme"]
    target = int(conf.get("target_chars", 20000))
    model = conf.get("text_model", "gemini-2.5-pro")
    style = conf.get("style", "")

    raw = _text(c, model,
                f'テーマ「{theme}」で長文note記事の構成案をJSONのみで返す（説明やコードフェンス不要）:\n'
                '{"title":"30字前後の魅力的なタイトル","sections":["見出し1",...8〜12個]}\n'
                f"本文合計 約{target}字想定。スタイル:{style}")
    raw = re.sub(r"^```[a-zA-Z]*|```$", "", raw.strip()).strip()
    try:
        o = json.loads(raw)
        title, sections = o["title"], o["sections"]
    except Exception:
        title, sections = theme, [f"{theme}のポイント{i}" for i in range(1, 9)]

    per = max(800, target // max(1, len(sections)))
    parts, total = [], 0
    for h in sections:
        p = _text(c, model,
                  f'記事「{title}」（テーマ:{theme}）の節「{h}」を約{per}字で執筆。'
                  f'見出しは「## {h}」で開始。具体例・体験談を入れる。前置き禁止・本文のみ。スタイル:{style}')
        if not p.lstrip().startswith("#"):
            p = f"## {h}\n\n{p}"
        parts.append(p)
        total += len(p)
        if total >= target:
            break
    body = f"# {title}\n\n" + "\n\n".join(parts) + "\n"

    thumb = None
    if conf.get("thumbnail", True):
        try:
            res = c.models.generate_images(
                model=conf.get("image_model", "imagen-3.0-generate-002"),
                prompt=f"note記事のアイキャッチ。テーマ「{theme}」、タイトル「{title}」。文字なし。清潔感のあるモダンな雰囲気。16:9。",
                config=types.GenerateImagesConfig(number_of_images=1, aspect_ratio="16:9"))
            img = res.generated_images[0].image
            data = getattr(img, "image_bytes", None) or img.read()
            d0 = OUT / dt.date.today().isoformat() / _slug(title)
            d0.mkdir(parents=True, exist_ok=True)
            thumb = d0 / "thumbnail.png"
            thumb.write_bytes(data)
        except Exception as e:
            print(f"[warn] サムネ生成失敗（記事は続行）: {e}")

    d = OUT / dt.date.today().isoformat() / _slug(title)
    d.mkdir(parents=True, exist_ok=True)
    (d / "article.md").write_text(body, encoding="utf-8")
    print(f"[gen] 生成: {title}（{len(body)}字）")
    return {"title": title, "body": body, "thumb": str(thumb) if thumb else None}


# ===================== 投稿（Playwright） =====================
def _md_plain(md: str) -> str:
    lines = []
    for ln in md.splitlines():
        if ln.startswith("# "):
            continue
        ln = re.sub(r"^#{2,6}\s*", "", ln)
        ln = re.sub(r"\*\*(.+?)\*\*", r"\1", ln)
        lines.append(ln)
    return "\n".join(lines).strip()


def _first(page: Page, sels, timeout=8000):
    last = None
    for s in sels:
        try:
            el = page.locator(s).first
            el.wait_for(state="visible", timeout=timeout)
            return el
        except PWTimeout as e:
            last = e
    raise PWTimeout(f"見つからない: {sels}") from last


def ensure_login(ctx) -> None:
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto("https://note.com/", wait_until="domcontentloaded")
    page.wait_for_timeout(2500)
    ok = page.evaluate("""async()=>{try{const r=await fetch('/api/v2/current_user');
        if(!r.ok)return false;const j=await r.json();return !!(j&&j.data&&j.data.id);}catch(e){return false;}}""")
    if not ok:
        print("\n▶ 開いたChromeで note にログインしてください（Googleでログインでお手元のスマホ認証等もOK）。")
        page.goto("https://note.com/login")
        input("  ログインが終わったら、このターミナルで Enter > ")


def post(ctx, art, conf) -> None:
    title = art["title"]
    body = _md_plain(art["body"])
    publish = bool(conf.get("publish"))
    page = ctx.new_page()
    page.goto(EDITOR_URL, wait_until="domcontentloaded")
    page.wait_for_timeout(3500)

    # タイトル
    tb = _first(page, ['textarea[placeholder*="タイトル"]', 'input[placeholder*="タイトル"]',
                       '[contenteditable="true"][aria-label*="タイトル"]', 'textarea'])
    tb.click()
    page.keyboard.type(title)

    # 本文
    bb = _first(page, ['div[contenteditable="true"][role="textbox"]',
                       'div.ProseMirror[contenteditable="true"]', '[contenteditable="true"]'])
    bb.click()
    for para in [x for x in body.split("\n") if x.strip()]:
        page.keyboard.insert_text(para)
        page.keyboard.press("Enter")
        page.keyboard.press("Enter")
    page.wait_for_timeout(1500)

    # サムネ
    if art.get("thumb") and Path(art["thumb"]).exists():
        try:
            page.set_input_files('input[type="file"]', art["thumb"])
            page.wait_for_timeout(2500)
            for lb in ["保存", "適用", "完了", "決定"]:
                try:
                    page.locator(f'button:has-text("{lb}")').first.click(timeout=2000)
                    break
                except Exception:
                    pass
        except Exception as e:
            print(f"[warn] サムネ添付スキップ: {e}")

    if not publish:
        page.wait_for_timeout(2000)   # noteは自動で下書き保存
        print(f"[post] 下書き保存: {title}")
        page.close()
        return

    _first(page, ['button:has-text("公開に進む")', 'button:has-text("公開")']).click()
    page.wait_for_timeout(1500)
    try:
        ti = _first(page, ['input[placeholder*="ハッシュタグ"]', 'input[placeholder*="タグ"]'], timeout=3500)
        for t in conf.get("tags", []):
            ti.click(); ti.type(t.lstrip("#")); page.keyboard.press("Enter")
    except PWTimeout:
        pass
    _first(page, ['button:has-text("投稿する")', 'button:has-text("公開する")', 'button:has-text("公開")']).click()
    page.wait_for_timeout(4000)
    print(f"[post] 公開: {title}")
    page.close()


# ===================== 1日の上限カウント =====================
def _today() -> int:
    if STATE.exists():
        try:
            d = json.loads(STATE.read_text(encoding="utf-8"))
            if d.get("date") == dt.date.today().isoformat():
                return int(d.get("count", 0))
        except Exception:
            pass
    return 0


def _bump():
    OUT.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps({"date": dt.date.today().isoformat(), "count": _today() + 1}), encoding="utf-8")


# ===================== メイン =====================
def cycle(conf) -> None:
    """1サイクル: ブラウザを開いて、上限まで生成→投稿。"""
    max_per_day = int(conf.get("max_per_day", 3))
    if _today() >= max_per_day:
        print(f"[stop] 本日の上限 {max_per_day} 件に到達。")
        return
    c = gem()
    with sync_playwright() as p:
        try:
            ctx = p.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE), channel="chrome",
                headless=bool(conf.get("headless", False)), user_agent=UA,
                viewport={"width": 1280, "height": 900},
                args=["--disable-blink-features=AutomationControlled"])
        except Exception:
            ctx = p.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE), headless=bool(conf.get("headless", False)),
                user_agent=UA, viewport={"width": 1280, "height": 900})
        try:
            ensure_login(ctx)
            page0 = ctx.pages[0] if ctx.pages else ctx.new_page()
            if str(conf.get("theme", "")).strip().lower() in ("auto", ""):
                conf["theme"] = detect_theme(c, conf, page0)
            for _ in range(int(conf.get("articles_per_run", 1))):
                if _today() >= max_per_day:
                    print(f"[stop] 上限 {max_per_day} 件に到達。"); break
                try:
                    art = generate(c, conf)
                    post(ctx, art, conf)
                    _bump()
                except Exception:
                    print(f"[error]\n{traceback.format_exc()}")
        finally:
            ctx.close()


def main():
    conf = load_cfg()
    if not bool(conf.get("loop", False)):
        cycle(conf)
        return
    iv = max(5, int(conf.get("interval_minutes", 180)))
    print(f"[loop] PC起動中、{iv}分ごとに実行 / 1日最大 {conf.get('max_per_day', 3)} 件。停止は Ctrl+C。")
    while True:
        try:
            cycle(conf)
        except Exception:
            print(f"[error-loop]\n{traceback.format_exc()}")
        time.sleep(iv * 60)


if __name__ == "__main__":
    main()
