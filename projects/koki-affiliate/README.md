# koki-affiliate — 全自動アフィリエイト記事ジェネレーター

シードキーワードを渡すと、**キーワード展開 → 記事生成 → アフィリリンク差し込み → 静的サイト出力**
までを全自動で実行します。**積み上げ式**なので、毎日走らせるほど記事が増えていきます。
出力はそのまま GitHub Pages で公開できます。

```
seeds.txt ──▶ キーワード展開 ──▶ 記事生成 ──▶ CTA差し込み ──▶ content/(JSON, 永続)
                (Claude/fallback)  (Claude/fallback)              │
                                                                  ▼
                                                    docs/(HTML, contentから再生成)
```

## 2つの動作モード

| モード | 条件 | 中身 |
|------|------|------|
| **Claude（本番）** | `anthropic` 導入 ＋ `ANTHROPIC_API_KEY` 設定 | Claude が本物のSEO記事を生成 |
| **テンプレ（fallback）** | 上記が無い場合 | 構造化テンプレで生成（**完全オフラインで動く**） |

## データの持ち方（積み上げの仕組み）

| 場所 | 役割 |
|------|------|
| `content/*.json` | 記事の**元データ（永続）**。実行のたびに新規記事だけ追記される |
| `docs/*.html` | 公開用サイト。毎回 `content/` 全体から再生成される |

同じキーワードは二度生成しません（slug で判定）。だから毎日回しても重複せず積み上がります。

## 使い方

```bash
cd projects/koki-affiliate

# オフラインで動作確認（キー不要・積み上げ式）
PYTHONPATH=src python -m affiliate.cli run --seed "ロボット掃除機" --count 3 --out docs --content content

# シードを複数 / ファイルから
PYTHONPATH=src python -m affiliate.cli run --seeds-file seeds.txt --count 5 --out docs --content content

# 保存済み記事からサイトだけ再ビルド
PYTHONPATH=src python -m affiliate.cli build --content content --out docs

# キーワード展開だけ見る
PYTHONPATH=src python -m affiliate.cli keywords --seed "ロボット掃除機" --count 10
```

`docs/index.html` をブラウザで開けば記事一覧が見られます。

## 本番（Claudeで生成）

```bash
pip install -e ".[llm]"
export ANTHROPIC_API_KEY=sk-ant-...
cp config.example.toml config.toml          # amazon_tag / site_url などを編集
affiliate run --seeds-file seeds.txt --count 5 --config config.toml
```

> モックでの検証用テスト（`tests/test_llm.py`）で、Claudeが返すJSONを正しく記事化する
> 経路は確認済みです。キーを入れればそのまま本番生成に切り替わります。

## 永遠に自動で公開する（GitHub Actions・推奨）

`/.github/workflows/affiliate-daily.yml` が毎日（07:00 JST）:

1. `seeds.txt` から未生成キーワードを選んで記事生成
2. `content/` に追記コミット（積み上げを永続化）
3. GitHub Pages へ公開

**セットアップ:**

1. Settings → Secrets and variables → Actions
   - **Secret**: `ANTHROPIC_API_KEY`（必須）
   - **Variables**（任意）: `SITE_URL`, `AMAZON_TAG`
2. Settings → **Pages** → Source = **GitHub Actions**
3. ワークフローをデフォルトブランチ（main）に置くとスケジュール実行されます。
   手動実行は Actions タブ → このワークフロー → **Run workflow**。

> 自分のPCを起動しておく必要はありません。クラウド側で毎日回ります。

## 自前サーバーで回す場合（cron）

```bash
0 7 * * * cd /path/koki-affiliate && ANTHROPIC_API_KEY=sk-ant-... \
  python -m affiliate.cli run --seeds-file seeds.txt --count 5 --config config.toml \
  && git add content docs && git commit -m "auto update" && git push
```

## ⚠️ 量産する前に知っておくこと（正直な注意）

- **「記事数 = 収益」ではありません。** Google は中身の薄い自動生成サイトをスパム評価で
  圏外に飛ばします。**量産だけのサイトはむしろ飛ばされる側**です。
- 勝ち筋は **ニッチ特化 ×（生成は自動・公開前に独自情報や一次データを足す）半自動**。
  本ツールは生成の自動化（土台）であって、独自性は人が乗せる前提です。
- **ステマ規制（2023.10〜）対応**として、CTAに「PR / 広告」表記、リンクに
  `rel="nofollow sponsored"`、フッターに開示文を入れています。**この表示は消さないでください。**
- Amazonアソシエイト等、各ASPの規約（虚偽の体験談・効果効能の断定の禁止など）も必ず確認を。

## 構成

```
src/affiliate/
  config.py     設定（TOML, stdlibのみ）
  llm.py        Claude呼び出し（無ければfallback）
  keywords.py   シード→ロングテール展開
  generate.py   記事生成（Claude/テンプレ）＋ slug
  affiliate.py  アフィリリンク組み立て＋CTA差し込み
  markdown.py   依存ゼロの Markdown→HTML
  store.py      記事の永続化（content/*.json の保存・読込）
  render.py     静的サイト出力（index/記事/css/sitemap/robots）
  pipeline.py   オーケストレーション（run=積み上げ / build=再生成）
  cli.py        CLI（run / build / keywords）
tests/          unittest（26件・標準ライブラリのみで実行可）
```

## テスト

```bash
PYTHONPATH=src python -m unittest discover -s tests -p "test_*.py"
```

## 次の一手（ロードマップ）

- WordPress / microCMS への自動投稿（REST API）
- アイキャッチ画像の自動生成・挿入
- 検索順位トラッキングと、伸びない記事の自動リライト
- 一次情報（価格API・スペック表・自前レビュー）の取り込みで独自性を担保
