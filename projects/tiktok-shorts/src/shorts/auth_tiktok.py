"""TikTok OAuth（1アカウント運用）: 連携・トークン保存・自動更新。

アクセストークンは約24時間で失効するため、リフレッシュトークン（約365日）で
自動更新し、保存ファイル(.tiktok_tokens.json)に保持する。

必要な環境変数（.env）:
  TIKTOK_CLIENT_KEY     アプリのクライアントキー
  TIKTOK_CLIENT_SECRET  アプリのクライアントシークレット
  TIKTOK_REDIRECT_URI   アプリに登録したリダイレクトURI（完全一致）
任意:
  TIKTOK_ACCESS_TOKEN   手動で固定トークンを使う場合（あれば最優先）
  TIKTOK_TOKEN_STORE    トークン保存先（既定 .tiktok_tokens.json）
"""
from __future__ import annotations

import json
import os
import time
import urllib.parse
from pathlib import Path

AUTH_BASE = "https://www.tiktok.com/v2/auth/authorize/"
TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
DEFAULT_SCOPES = "user.info.basic,video.upload,video.publish"


def _requests():
    try:
        import requests
        return requests
    except ImportError as e:  # pragma: no cover
        raise RuntimeError("requests が未インストールです: pip install requests") from e


def _store_path() -> Path:
    return Path(os.environ.get("TIKTOK_TOKEN_STORE", ".tiktok_tokens.json"))


def _app() -> tuple[str, str, str]:
    ck = os.environ.get("TIKTOK_CLIENT_KEY")
    cs = os.environ.get("TIKTOK_CLIENT_SECRET")
    ru = os.environ.get("TIKTOK_REDIRECT_URI")
    missing = [n for n, v in [("TIKTOK_CLIENT_KEY", ck),
                              ("TIKTOK_CLIENT_SECRET", cs),
                              ("TIKTOK_REDIRECT_URI", ru)] if not v]
    if missing:
        raise RuntimeError(f"未設定の環境変数: {', '.join(missing)}（.env を確認）")
    return ck, cs, ru  # type: ignore[return-value]


def _save(tokens: dict) -> dict:
    tokens["_obtained_at"] = time.time()
    p = _store_path()
    p.write_text(json.dumps(tokens, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        os.chmod(p, 0o600)  # トークンは機密。所有者のみ読み書き
    except OSError:
        pass
    return tokens


def _load() -> dict | None:
    p = _store_path()
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def authorize_url(scopes: str = DEFAULT_SCOPES, state: str = "koki") -> str:
    ck, _, ru = _app()
    q = urllib.parse.urlencode({
        "client_key": ck,
        "scope": scopes,
        "response_type": "code",
        "redirect_uri": ru,
        "state": state,
    })
    return f"{AUTH_BASE}?{q}"


def parse_code(raw: str) -> str:
    """リダイレクトURL全体でも、code単体でも受け取れるようにする。"""
    raw = raw.strip()
    if "code=" in raw:
        qs = urllib.parse.urlparse(raw).query
        code = urllib.parse.parse_qs(qs).get("code", [""])[0]
        # URLデコード（末尾の #_ などTikTok特有の付与を除去）
        return code.split("#")[0] or raw
    return raw


def exchange_code(code: str) -> dict:
    ck, cs, ru = _app()
    requests = _requests()
    r = requests.post(TOKEN_URL, headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "Cache-Control": "no-cache",
    }, data={
        "client_key": ck,
        "client_secret": cs,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": ru,
    }, timeout=30)
    r.raise_for_status()
    data = r.json()
    if "access_token" not in data:
        raise RuntimeError(f"トークン取得失敗: {data}")
    return _save(data)


def refresh() -> dict:
    t = _load()
    if not t or not t.get("refresh_token"):
        raise RuntimeError("リフレッシュトークンがありません。`shorts auth url` で連携し直してください。")
    ck, cs, _ = _app()
    requests = _requests()
    r = requests.post(TOKEN_URL, headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "Cache-Control": "no-cache",
    }, data={
        "client_key": ck,
        "client_secret": cs,
        "grant_type": "refresh_token",
        "refresh_token": t["refresh_token"],
    }, timeout=30)
    r.raise_for_status()
    data = r.json()
    if "access_token" not in data:
        raise RuntimeError(f"トークン更新失敗: {data}")
    t.update(data)
    return _save(t)


def valid_access_token() -> str:
    """常に有効なアクセストークンを返す（必要なら自動更新）。"""
    env_tok = os.environ.get("TIKTOK_ACCESS_TOKEN")
    if env_tok:
        return env_tok
    t = _load()
    if not t:
        raise RuntimeError(
            "未連携です。`PYTHONPATH=src python -m shorts auth url` で連携してください。")
    obtained = t.get("_obtained_at", 0)
    expires_in = t.get("expires_in", 0)
    if time.time() >= obtained + expires_in - 120:  # 期限2分前で先回り更新
        t = refresh()
    return t["access_token"]


def status_text() -> str:
    if os.environ.get("TIKTOK_ACCESS_TOKEN"):
        return "状態: 環境変数 TIKTOK_ACCESS_TOKEN を使用中（手動固定）。"
    t = _load()
    if not t:
        return "状態: 未連携。`shorts auth url` から連携してください。"
    remain = int(t.get("_obtained_at", 0) + t.get("expires_in", 0) - time.time())
    mark = "有効" if remain > 0 else "失効（次回利用時に自動更新）"
    return (f"状態: 連携済み ✅\n"
            f"  open_id : {t.get('open_id', '?')}\n"
            f"  scope   : {t.get('scope', '?')}\n"
            f"  access  : {mark}（残り約 {max(remain, 0)} 秒）\n"
            f"  store   : {_store_path()}")
