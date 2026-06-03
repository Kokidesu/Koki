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
# 1) システム依存: ffmpeg
sudo apt-get install -y ffmpeg        # mac: brew install ffmpeg

# 2) Python依存
cd projects/tiktok-shorts
pip install -r requirements.txt

# 3) 環境変数
cp .env.example .env                  # 中身を編集
cp config.example.yaml config.yaml    # ジャンル/本数/声などを編集
```

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

# 10本まとめて生成（投稿はしない）
python -m shorts batch -n 10

# フル実行: 調査→10本生成→公式APIで下書き投稿
python -m shorts run -n 10
```

出力は `out/` 配下に `動画.mp4` ＋ `manifest.json`（台本・字幕・投稿ステータス）として保存されます。

---

## 1日10投稿の運用

`run` 1回で10本まとめて下書きに上げ、人が確認して公開、が安全運用です。
完全自動の定期実行にしたい場合は cron（例: 朝に10本下書き生成）:

```cron
0 8 * * *  cd /path/to/projects/tiktok-shorts && PYTHONPATH=src python -m shorts run -n 10 >> run.log 2>&1
```

> リポジトリ内の `/loop` スキルでも定期実行できます。ただし **投稿頻度はアカウントの状態を見ながら** 調整してください（新規アカウントでいきなり10連投はスパム判定されやすい）。

---

## 公式API（Content Posting API）について

- 投稿は **本人認証した1アカウント** に対してOAuthトークンで行います。
- **下書き(inbox)** … スコープ `video.upload`。審査前でも使える最も安全なモード（既定）。
- **自動公開(direct)** … スコープ `video.publish`。**公開**するにはアプリ審査(audit)が必要。審査前は `SELF_ONLY`（自分だけ閲覧）でのみ可。
- 取得手順は https://developers.tiktok.com/ の Content Posting API を参照。

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
  pipeline.py      バッチ・オーケストレーション
  cli.py           コマンドライン
samples/           すぐ使えるサンプル（ネタ一覧・台本）
assets/            背景動画/BGMを置く場所（任意）
```
