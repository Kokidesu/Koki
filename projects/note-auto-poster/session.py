"""
session.py — note にログイン済みのブラウザ context を用意する共通処理。
Build a logged-in Playwright browser context for note.com.

ログイン情報の優先順位 / credential priority:
  1) 環境変数 NOTE_COOKIES_JSON … ブラウザ拡張 "Cookie-Editor" でエクスポートしたJSON
     （Googleログイン等でも、ログイン済みのCookieをそのまま使えるのでこれが一番確実）
  2) storage_state.json …… tools/export_note_session.py で作ったファイル
  3) NOTE_EMAIL / NOTE_PASSWORD … メール+パスワードでその場ログイン
"""
from __future__ import annotations

import json
import os
from pathlib import Path

HERE = Path(__file__).parent
STORAGE = HERE / "storage_state.json"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

_SAMESITE = {"no_restriction": "None", "none": "None", "lax": "Lax", "strict": "Strict"}


def _map_cookies(raw: list) -> list:
    """Cookie-Editor等のJSONを Playwright の add_cookies 形式へ変換。"""
    out = []
    for c in raw:
        if not c.get("name") or "value" not in c:
            continue
        ck = {
            "name": c["name"],
            "value": str(c["value"]),
            "domain": c.get("domain") or ".note.com",
            "path": c.get("path") or "/",
            "httpOnly": bool(c.get("httpOnly")),
            "secure": bool(c.get("secure")),
        }
        exp = c.get("expirationDate") or c.get("expires")
        if exp and not c.get("session"):
            try:
                ck["expires"] = float(exp)
            except (TypeError, ValueError):
                pass
        ss = c.get("sameSite")
        ss = _SAMESITE.get(str(ss).lower()) if ss else None
        if ss:
            ck["sameSite"] = ss
            if ss == "None":
                ck["secure"] = True
        out.append(ck)
    if not out:
        raise SystemExit("Cookieを1件も読み取れませんでした。NOTE_COOKIES_JSON の中身を確認してください。")
    return out


def make_context(p, headless: bool = True):
    """(browser, context) を返す。呼び出し側で両方 close すること。"""
    browser = p.chromium.launch(headless=headless)

    cookies_json = os.environ.get("NOTE_COOKIES_JSON", "").strip()
    if cookies_json:
        ctx = browser.new_context(user_agent=UA)
        try:
            raw = json.loads(cookies_json)
        except json.JSONDecodeError as e:
            raise SystemExit(f"NOTE_COOKIES_JSON がJSONとして読めません: {e}")
        if isinstance(raw, dict) and "cookies" in raw:   # storage_state形式も許容
            raw = raw["cookies"]
        ctx.add_cookies(_map_cookies(raw))
        return browser, ctx

    if STORAGE.exists() and STORAGE.stat().st_size > 5:
        return browser, browser.new_context(storage_state=str(STORAGE), user_agent=UA)

    email = os.environ.get("NOTE_EMAIL")
    pw = os.environ.get("NOTE_PASSWORD")
    if email and pw:
        ctx = browser.new_context(user_agent=UA)
        _login_email(ctx, email, pw)
        return browser, ctx

    raise SystemExit(
        "noteのログイン情報がありません。次のどれかをSecret/環境変数に設定してください:\n"
        "  - NOTE_COOKIES_JSON（Cookie-Editor拡張のエクスポート）← Googleログインの人はこれ\n"
        "  - NOTE_STORAGE_STATE（export_note_session.py で作成）\n"
        "  - NOTE_EMAIL と NOTE_PASSWORD（メール+パスワードの人）"
    )


def _login_email(ctx, email: str, pw: str) -> None:
    page = ctx.new_page()
    page.goto("https://note.com/login", wait_until="domcontentloaded")
    page.wait_for_timeout(1500)
    try:
        page.fill('input[type="email"], input[name="email"], input[name="login"]', email)
        page.fill('input[type="password"], input[name="password"]', pw)
        page.click('button:has-text("ログイン"), button[type="submit"]')
        page.wait_for_timeout(5000)
    finally:
        page.close()
