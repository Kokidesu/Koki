"""
export_note_session.py — note のログインセッションを1回だけ取り出すツール（手元のPCで実行）。
Run this ONCE on your own computer to capture a logged-in note session.

使い方 / how to:
  1) pip install playwright && python -m playwright install chromium
  2) python tools/export_note_session.py
  3) 開いたブラウザで note にログイン（メール/Google等、2段階認証も普通に通す）
  4) ログインできたらターミナルで Enter を押す
  → storage_state.json が保存される。

GitHub Actions で使うときは、この storage_state.json の中身を丸ごとコピーして
リポジトリの Secret `NOTE_STORAGE_STATE` に貼り付けてください。
※このファイルはログイン情報そのものです。絶対にコミット/共有しないこと（.gitignore済み）。
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent.parent / "storage_state.json"


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # 画面を表示してログインしてもらう
        ctx = browser.new_context()
        page = ctx.new_page()
        page.goto("https://note.com/login")
        print("\n▶ 開いたブラウザで note にログインしてください。")
        input("  ログインが完了したら、このターミナルで Enter を押す > ")
        ctx.storage_state(path=str(OUT))
        print(f"\n✅ 保存しました: {OUT}")
        print("   この中身を GitHub の Secret `NOTE_STORAGE_STATE` に貼り付ければ、PCを閉じても動きます。")
        browser.close()


if __name__ == "__main__":
    main()
