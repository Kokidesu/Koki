"""
post_note.py — 生成済みの記事を note に自動投稿する（Playwright）。
Auto-post a generated article to note.com using a logged-in browser session.

前提 / requires:
  storage_state.json … note にログイン済みのセッション。
                       先に tools/export_note_session.py で作成しておく。

⚠ 重要 / IMPORTANT:
  note には公式の投稿APIが無いため、ブラウザUIを自動操作しています。
  下のセレクタ（タイトル欄・本文欄・公開ボタン等）は note のUI変更で
  ずれることがあります。その場合は `playwright codegen https://note.com/notes/new`
  で実際のUIを見ながら微調整してください。
  （このスクリプトは note にアクセスできない隔離環境で書いたため、
    セレクタは“最も可能性が高い候補＋フォールバック”にしてあります。）
"""
from __future__ import annotations

import re
import time
from pathlib import Path

from playwright.sync_api import sync_playwright, Page, TimeoutError as PWTimeout

HERE = Path(__file__).parent
STORAGE = HERE / "storage_state.json"
EDITOR_URL = "https://note.com/notes/new"


def _md_to_plain(md: str) -> tuple[str, str]:
    """Markdownから (タイトル, 本文プレーンテキスト) を取り出す。"""
    lines = md.splitlines()
    title = ""
    body: list[str] = []
    for ln in lines:
        if not title and ln.startswith("# "):
            title = ln[2:].strip()
            continue
        ln = re.sub(r"^#{2,6}\s*", "", ln)        # 見出し記号を除去
        ln = re.sub(r"\*\*(.+?)\*\*", r"\1", ln)   # 太字記号を除去
        ln = re.sub(r"`([^`]*)`", r"\1", ln)
        body.append(ln)
    return title or "無題", "\n".join(body).strip()


def _first(page: Page, selectors: list[str], timeout: int = 8000):
    """候補セレクタを順に試し、最初に見つかった要素を返す。"""
    last = None
    for sel in selectors:
        try:
            el = page.locator(sel).first
            el.wait_for(state="visible", timeout=timeout)
            return el
        except PWTimeout as e:
            last = e
            continue
    raise PWTimeout(f"none of selectors matched: {selectors}") from last


def post_article(md_path: str, tags: list[str], publish: bool,
                 thumbnail: str | None = None, headless: bool = True) -> None:
    md = Path(md_path).read_text(encoding="utf-8")
    title, body = _md_to_plain(md)

    if not STORAGE.exists():
        raise SystemExit(
            "storage_state.json がありません。先に `python tools/export_note_session.py` で "
            "noteにログインしてセッションを保存してください。"
        )

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        ctx = browser.new_context(storage_state=str(STORAGE))
        page = ctx.new_page()
        page.goto(EDITOR_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)

        # --- タイトル ---
        title_box = _first(page, [
            'textarea[placeholder*="タイトル"]',
            'input[placeholder*="タイトル"]',
            '[contenteditable="true"][aria-label*="タイトル"]',
            'textarea',
        ])
        title_box.click()
        title_box.fill(title) if title_box.evaluate("e=>e.tagName")!="DIV" else page.keyboard.type(title)

        # --- 本文 ---
        body_box = _first(page, [
            'div[contenteditable="true"][role="textbox"]',
            'div.ProseMirror[contenteditable="true"]',
            '[contenteditable="true"]',
        ])
        body_box.click()
        # 大量テキストは段落ごとに挿入（insert_textはキーイベントを発火せず高速）
        for para in [x for x in body.split("\n") if x.strip() != ""]:
            page.keyboard.insert_text(para)
            page.keyboard.press("Enter")
            page.keyboard.press("Enter")
        page.wait_for_timeout(1500)  # 自動保存待ち

        # --- サムネ（任意・UI変動が大きいのでベストエフォート）---
        if thumbnail and Path(thumbnail).exists():
            try:
                _attach_thumbnail(page, thumbnail)
            except Exception as e:
                print(f"[warn] thumbnail upload skipped: {e}")

        if not publish:
            # 下書きはnoteが自動保存。明示ボタンがあれば押す。
            try:
                _first(page, ['button:has-text("下書き保存")'], timeout=4000).click()
            except PWTimeout:
                pass
            print(f"[ok] draft saved: {title}")
            page.wait_for_timeout(2000)
            ctx.close(); browser.close()
            return

        # --- 公開フロー ---
        _first(page, ['button:has-text("公開に進む")', 'button:has-text("公開")']).click()
        page.wait_for_timeout(1500)

        # ハッシュタグ入力（あれば）
        try:
            tag_input = _first(page, [
                'input[placeholder*="ハッシュタグ"]', 'input[placeholder*="タグ"]',
            ], timeout=4000)
            for t in tags:
                tag_input.click()
                tag_input.type(t.lstrip("#"))
                page.keyboard.press("Enter")
        except PWTimeout:
            pass

        # 最終の「投稿する/公開する」
        _first(page, [
            'button:has-text("投稿する")', 'button:has-text("公開する")',
            'button:has-text("公開")',
        ]).click()
        page.wait_for_timeout(4000)
        print(f"[ok] published: {title}")
        ctx.close(); browser.close()


def _attach_thumbnail(page: Page, path: str) -> None:
    """見出し画像を追加。ファイル入力を直接叩く方式。"""
    page.set_input_files('input[type="file"]', path)
    page.wait_for_timeout(2500)
    # トリミング確定ボタンがある場合
    for label in ["保存", "適用", "完了", "決定"]:
        try:
            page.locator(f'button:has-text("{label}")').first.click(timeout=2500)
            break
        except Exception:
            continue


if __name__ == "__main__":
    import sys, yaml
    cfg = yaml.safe_load((HERE / "config.yaml").read_text(encoding="utf-8"))
    md = sys.argv[1] if len(sys.argv) > 1 else None
    if not md:
        raise SystemExit("usage: python post_note.py <article.md>")
    post_article(md, cfg.get("tags", []), bool(cfg.get("publish")), headless=True)
