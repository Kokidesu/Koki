"""
detect_theme.py — あなたのnoteアカウントから「テーマ」を自動推定する。
Auto-detect the article theme by reading the account's own profile + recent
article titles (using your logged-in session), then summarizing with Gemini.

※ note はボット直アクセスを拒否するため、ログイン済みブラウザ(Playwright)の
  ページ内 fetch で同一オリジンAPIを叩いて取得する（これが一番通る）。
"""
from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
STORAGE = HERE / "storage_state.json"

_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def _urlname(account_url: str) -> str:
    return urlparse(account_url).path.strip("/").split("/")[0]


def fetch_account_text(account_url: str) -> dict:
    """プロフィール文と直近の記事タイトルを集める。"""
    urlname = _urlname(account_url)
    from session import make_context
    with sync_playwright() as p:
        browser, ctx = make_context(p, headless=True)
        page = ctx.new_page()
        page.goto(f"https://note.com/{urlname}", wait_until="domcontentloaded")
        page.wait_for_timeout(2000)
        data = page.evaluate(
            """async (urlname) => {
                const out = { bio: '', titles: [] };
                try {
                    const r = await fetch(`/api/v2/creators/${urlname}`);
                    if (r.ok) {
                        const d = (await r.json()).data || {};
                        out.bio = [d.nickname, d.profile, d.description]
                            .filter(Boolean).join('\\n');
                    }
                } catch (e) {}
                try {
                    const r = await fetch(`/api/v2/creators/${urlname}/contents?kind=note&page=1`);
                    if (r.ok) {
                        const d = (await r.json()).data || {};
                        out.titles = (d.contents || []).map(c => c.name).filter(Boolean);
                    }
                } catch (e) {}
                return out;
            }""",
            urlname,
        )
        ctx.close()
        browser.close()
    return data


def detect_theme(cfg: dict) -> str:
    info = fetch_account_text(cfg["account_url"])
    titles = info.get("titles") or []
    bio = info.get("bio") or ""
    if not titles and not bio:
        raise SystemExit(
            "アカウントから記事/プロフを取得できませんでした。\n"
            "（ログインセッション切れ or note仕様変更の可能性）。\n"
            "→ config.yaml の theme を手動で設定するか、export_note_session.py を取り直してください。"
        )

    from google import genai
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    prompt = (
        "次のnoteアカウントのプロフィールと記事タイトルを見て、"
        "このアカウントが今後書くべき記事の『テーマ』を日本語の1文で簡潔に表してください。"
        "前置きや説明は不要、テーマの一文だけを返す。\n\n"
        f"プロフィール:\n{bio}\n\n記事タイトル:\n- " + "\n- ".join(titles)
    )
    resp = client.models.generate_content(
        model=cfg.get("text_model", "gemini-2.5-pro"), contents=prompt
    )
    theme = (resp.text or "").strip().strip("「」\"' 　")
    out = HERE / "output"
    out.mkdir(exist_ok=True)
    (out / "detected_theme.txt").write_text(theme + "\n", encoding="utf-8")
    print(f"[ok] アカウントから推定したテーマ: {theme}")
    print(f"     （参考にした記事タイトル {len(titles)}件）")
    return theme


if __name__ == "__main__":
    import yaml
    cfg = yaml.safe_load((HERE / "config.yaml").read_text(encoding="utf-8"))
    print(detect_theme(cfg))
