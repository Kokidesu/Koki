"""TikTok 公式 Content Posting API クライアント（本人認証した1アカウント用）。

- draft : /v2/post/publish/inbox/video/init/  … 下書き(inbox)へ。スコープ video.upload。審査前でも可（最も安全・既定）。
- direct: /v2/post/publish/video/init/        … 自動公開。スコープ video.publish。公開には審査(audit)が必要。
                                                  審査前は privacy=SELF_ONLY のみ許可。

トークンは引数 or 環境変数 TIKTOK_ACCESS_TOKEN。取得は https://developers.tiktok.com/ を参照。
"""
from __future__ import annotations

from pathlib import Path

BASE = "https://open.tiktokapis.com/v2"


def _requests():
    try:
        import requests
        return requests
    except ImportError as e:  # pragma: no cover
        raise RuntimeError("requests が未インストールです: pip install requests") from e


def _token(token: str | None) -> str:
    if token:
        return token
    # 明示トークンが無ければ OAuth ストア（環境変数→保存トークン、必要なら自動更新）から取得
    from .auth_tiktok import valid_access_token
    return valid_access_token()


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=UTF-8"}


def creator_info(token: str | None = None) -> dict:
    requests = _requests()
    r = requests.post(f"{BASE}/post/publish/creator_info/query/", headers=_headers(_token(token)), timeout=30)
    r.raise_for_status()
    return r.json()


def _init_and_upload(endpoint: str, body: dict, video_path: str, token: str) -> str:
    requests = _requests()
    size = Path(video_path).stat().st_size
    body["source_info"] = {
        "source": "FILE_UPLOAD",
        "video_size": size,
        "chunk_size": size,          # 1チャンクで丸ごと（ショート動画なら十分）
        "total_chunk_count": 1,
    }
    r = requests.post(endpoint, headers=_headers(token), json=body, timeout=60)
    r.raise_for_status()
    data = r.json()
    if data.get("error", {}).get("code") not in (None, "ok"):
        raise RuntimeError(f"init失敗: {data['error']}")
    info = data["data"]
    publish_id, upload_url = info["publish_id"], info["upload_url"]

    with open(video_path, "rb") as f:
        payload = f.read()
    put_headers = {
        "Content-Type": "video/mp4",
        "Content-Length": str(size),
        "Content-Range": f"bytes 0-{size - 1}/{size}",
    }
    pr = requests.put(upload_url, headers=put_headers, data=payload, timeout=300)
    pr.raise_for_status()
    return publish_id


def upload_draft(video_path: str, token: str | None = None) -> str:
    """下書き(inbox)へアップロード。ユーザーがアプリ通知から公開する。"""
    return _init_and_upload(
        f"{BASE}/post/publish/inbox/video/init/", {}, video_path, _token(token)
    )


def post_direct(video_path: str, title: str = "", privacy: str = "SELF_ONLY",
                token: str | None = None) -> str:
    """直接投稿（公開）。公開には審査が必要。審査前は privacy=SELF_ONLY のみ。"""
    body = {
        "post_info": {
            "title": title[:2200],
            "privacy_level": privacy,
            "disable_comment": False,
            "disable_duet": False,
            "disable_stitch": False,
        }
    }
    return _init_and_upload(
        f"{BASE}/post/publish/video/init/", body, video_path, _token(token)
    )


def fetch_status(publish_id: str, token: str | None = None) -> dict:
    requests = _requests()
    r = requests.post(
        f"{BASE}/post/publish/status/fetch/",
        headers=_headers(_token(token)),
        json={"publish_id": publish_id},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def publish(video_path: str, mode: str = "draft", title: str = "",
            privacy: str = "SELF_ONLY", token: str | None = None) -> dict:
    """mode に応じて投稿し、結果dictを返す。"""
    tok = _token(token)
    if mode == "draft":
        pid = upload_draft(video_path, tok)
    elif mode == "direct":
        pid = post_direct(video_path, title, privacy, tok)
    else:
        raise ValueError(f"未知の mode: {mode}")
    return {"mode": mode, "publish_id": pid}
