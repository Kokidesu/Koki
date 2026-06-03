# tiktok-shorts — 雑学ショート動画 量産パイプライン

雑学・豆知識のTikTokショート（9:16 縦型動画）を **バッチで量産** し、
**TikTok公式 Content Posting API** で投稿（既定は安全な「下書き」アップロード）まで行うツールです。

```
トレンド調査 → 台本生成(Claude) → AI音声(TTS) → 自動字幕 → 動画合成(ffmpeg) → 公式APIで下書き投稿
```

---

## ⚠️ はじめに（重要なルール）

このツールは **「本物のアカウント 1〜数個」を健全に運用する** ためのものです。
次のことは **やりません／できません**。意図的にそう設計しています。

- ❌ **アカウントの自動・大量作成** … TikTok規約違反。アカウント群ごと一括BANされ、シャドウバンで再生数も死にます。
- ❌ **複数アカウントの協調的スパム投稿** … 同上。
- ❌ **ブラウザ自動操作での投稿** … 規約違反・BANリスク。本ツールは公式APIのみ使用します。

> TikTokの再生数は「アカウント数」ではなく **1本ごとの視聴維持率（watch time）** で決まります。
> 1〜数アカウントに集中し、トレンドに沿った質の高い動画を継続投稿するのが、結局いちばん伸びます。

また雑学ジャンルは **事実の正確さ** が命です。生成された台本は **投稿前に必ずファクトチェック** してください。

---

## できること

- 🔎 **トレンド調査** … いま伸びている雑学の切り口をClaudeでリサーチしてネタ出し
- ✍️ **台本生成** … フック→本編→CTA の構成で日本語ナレーション原稿を一括生成
- 🔊 **AI音声(TTS)** … 既定は無料の `edge-tts`（APIキー不要）。ElevenLabs等にも差し替え可
- 💬 **自動字幕** … TTSの単語タイムスタンプから字幕(ASS)を自動生成・焼き込み
- 🎬 **動画合成** … 背景＋音声＋字幕を 1080x1920 の縦型MP4に（ffmpeg）
- 📤 **公式API投稿** … 既定は「下書き(inbox)」アップロード。審査後は自動公開(direct)も可
- 🔁 **バッチ実行** … `run` で「調査→10本生成→下書き投稿」を一気に

---

## セットアップ

```bash
# 1) Python依存（ffmpeg が無くても static-ffmpeg が自動で入る）
cd projects/tiktok-shorts
pip install -r requirements.txt

# 2) (任意) システムにffmpegを入れると高速・安定
#    Ubuntu: sudo apt-get install -y ffmpeg / mac: brew install ffmpeg

# 3) 環境変数と設定
cp .env.example .env                  # 中身を編集
cp config.example.yaml config.yaml    # ジャンル/本数/声/フォントなど

# 4) まず環境チェック
PYTHONPATH=src python -m shorts doctor
```

> **日本語フォントが必要**: 字幕の焼き込みにCJKフォントを使います。`doctor` でフォントの有無は分かりませんが、
> 文字が□になる場合は CJKフォント（Noto Sans CJK JP / IPAGothic 等）を入れ、`config.yaml` の `font` を合わせるか、
> `assets/fonts/` に .ttf/.otf を置いてください。

必要なキー（`.env`）:

| 変数 | 用途 |
| --- | --- |
| `ANTHROPIC_API_KEY` | 台本・トレンド調査（必須） |
| `TIKTOK_ACCESS_TOKEN` | 公式API投稿用。TikTok for Developers のOAuthで取得 |

> TTSは既定で **edge-tts（キー不要・無料）** を使うので、最初の動画生成だけなら `ANTHROPIC_API_KEY` だけでOKです。

---

## 使い方

```bash
export PYTHONPATH=src

# トレンド調査だけ（ネタ一覧をJSONで出力）
python -m shorts research -n 10

# 台本を1本だけ確認
python -m shorts script "バナナは放射性物質を含む"

# 動画を1本作る（台本→音声→字幕→MP4）
python -m shorts make "ハチミツは腐らない"

# 保存済みの台本JSONから作る（手書き台本もOK）
python -m shorts render samples/scripts/01_banana.json

# 10本まとめて生成（投稿はしない）
python -m shorts batch -n 10

# フル実行: 調査→10本生成→公式APIで下書き投稿
python -m shorts run -n 10

# 環境・連携状態のチェック
python -m shorts doctor
```

> **今日から試す（投稿なし）**: TikTok連携が未完了でも、`ANTHROPIC_API_KEY` だけ設定すれば
> `batch` / `make` / `render` で動画は量産できます。中身を確認してから連携→投稿に進むのが安全です。

出力は `out/` 配下に `動画.mp4` ＋ `manifest.json`（台本・字幕・投稿ステータス）として保存されます。

---

## 1日10投稿の運用

`run` 1回で10本まとめて下書きに上げ、人が確認して公開、が安全運用です。
定期実行は用途に合わせて選べます:

- **cron / systemd（推奨）** … 手元PCやVPSで毎朝自動生成。`scripts/run_daily.sh` を使い、
  `deploy/crontab.example` か `deploy/shorts-daily.{service,timer}` を参照。トークンが永続化され投稿まで自動化できる。
  ```bash
  ./scripts/run_daily.sh 10        # 10本生成→設定どおり下書き投稿
  ```
- **GitHub Actions** … `.github/workflows/tiktok-shorts-generate.yml`。CIで生成して成果物を
  ダウンロードできる（**投稿はしない**。CIはトークン永続化が不安定なため生成専用）。

> **投稿頻度はアカウントの状態を見ながら**調整してください。新規アカウントでいきなり10連投は
> スパム判定されやすいので、最初は1日3〜5本から徐々に増やすのが安全です。

---

## アカウント連携（1アカウント運用 / OAuth）

投稿は **本人認証した1アカウント** に対して公式APIトークンで行います。
アクセストークンは約24時間で失効しますが、**リフレッシュトークンで自動更新**するので一度連携すれば回り続けます。

**準備（TikTok for Developers）**
1. https://developers.tiktok.com/ でアプリを作成し、**Content Posting API** を追加。
2. **Login Kit** のスコープに `video.upload`（下書き用）と、必要なら `video.publish`（自動公開用）を追加。
3. **Redirect URI** を登録（例: `https://example.com/callback`）。`.env` の `TIKTOK_REDIRECT_URI` と完全一致させる。
4. `.env` に `TIKTOK_CLIENT_KEY` / `TIKTOK_CLIENT_SECRET` / `TIKTOK_REDIRECT_URI` を設定。

**連携する**
```bash
export PYTHONPATH=src
python -m shorts auth url                       # 表示されたURLをブラウザで開いて承認
python -m shorts auth login "<リダイレクト先URL>"  # ?code=... 付きURLを丸ごと貼る
python -m shorts auth status                    # 連携状態を確認
```
以後 `run` / `make --publish draft` の投稿時に自動でトークンを使い、失効時は自動更新します。
トークンは `.tiktok_tokens.json`（gitignore済み・**他人に渡さない**）に保存されます。

**投稿モード**
- **下書き(inbox)** … スコープ `video.upload`。審査前でも使える最も安全なモード（既定）。アプリ通知から自分で公開。
- **自動公開(direct)** … スコープ `video.publish`。**公開**にはアプリ審査(audit)が必要。審査前は `SELF_ONLY`（自分のみ閲覧）でのみ可。

---

## 構成

```
src/shorts/
  trends.py        トレンド調査（Claude / 任意で検索API）
  script.py        雑学ナレーション台本の生成
  tts.py           TTS（既定 edge-tts、差し替え可）+ 単語タイムスタンプ
  subtitles.py     タイムスタンプ→字幕(ASS)生成
  video.py         ffmpegで縦型MP4合成（字幕焼き込み）
  publish_tiktok.py 公式Content Posting APIクライアント（下書き/公開）
  auth_tiktok.py   OAuth連携・トークン保存/自動更新（1アカウント）
  pipeline.py      バッチ・オーケストレーション
  cli.py           コマンドライン（research/script/make/render/batch/run/auth/doctor）
samples/           すぐ使えるサンプル（ネタ一覧・台本）
assets/            背景動画/BGM/フォントを置く場所（任意）
scripts/           run_daily.sh（定期実行ラッパ）
deploy/            cron / systemd の設定例
docs/              SETUP_TIKTOK.md（API連携の手順）
```
