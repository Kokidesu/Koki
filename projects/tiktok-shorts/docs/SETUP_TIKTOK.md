# TikTok 公式API 連携セットアップ（1アカウント）

このツールの投稿は **TikTok Content Posting API** を使います。
ここでは「下書き(draft)に自動アップ」まで通すための最短手順をまとめます。

## 1. 開発者アプリを作る
1. https://developers.tiktok.com/ にTikTokアカウントでログイン。
2. **Manage apps → Connect an app**（アプリ作成）。
3. アプリに **Products** として **Content Posting API** を追加。
4. **Login Kit** を追加し、**Scopes** に以下を有効化:
   - `user.info.basic`
   - `video.upload`（下書きアップロードに必須）
   - `video.publish`（自動公開もしたい場合。公開には後述の審査が必要）

## 2. リダイレクトURIを登録
- アプリ設定の **Redirect URI** に1つ登録する（例 `https://example.com/callback`）。
- 自分専用なら値は何でもよいが、`.env` の `TIKTOK_REDIRECT_URI` と **完全一致** させること。
- 承認後、その URL に `?code=...` が付いて飛ぶので、それを丸ごとコピーして使う。

## 3. .env を設定
```
TIKTOK_CLIENT_KEY=（アプリのClient key）
TIKTOK_CLIENT_SECRET=（アプリのClient secret）
TIKTOK_REDIRECT_URI=https://example.com/callback
ANTHROPIC_API_KEY=sk-ant-...
```

## 4. 連携する
```bash
cd projects/tiktok-shorts
export PYTHONPATH=src
python -m shorts auth url                        # 出たURLをブラウザで開いて承認
python -m shorts auth login "<飛んだ先のURL>"      # ?code=... 付きURLを丸ごと貼る
python -m shorts auth status                     # 「連携済み ✅」を確認
```
これで `.tiktok_tokens.json` にトークンが保存され、失効しても自動更新されます。

## 5. 投稿する
```bash
python -m shorts run -n 10            # 10本生成 → 下書き(draft)へ自動アップ
```
TikTokアプリの通知（または「下書き」）から内容を確認して公開してください。

## よくあるハマりどころ
- **`redirect_uri` mismatch** … `.env` の値とアプリ登録値が1文字でも違うと失敗。完全一致に。
- **scope不足エラー** … `video.upload` が無いと下書きできない。アプリでスコープ追加 → 連携やり直し。
- **公開(direct)できない** … 公開は審査(audit)が必要。審査前は `config.yaml` の `publish.mode: draft`、
  または `direct` でも `privacy: SELF_ONLY` のみ。まずは draft 運用が安全。
- **詰まったら** … `python -m shorts doctor` で環境と連携状態をまとめて確認できます。
