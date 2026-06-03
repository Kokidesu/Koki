# koki-affiliate — 全自動アフィリエイト記事ジェネレーター

シードキーワードから **キーワード展開 → 記事生成 → アイキャッチ画像 → アフィリリンク差し込み
→ 静的サイト出力** までを全自動で実行します。**積み上げ式**なので、走らせるほど記事が増えます。
出力はそのまま GitHub Pages で公開できます。

```
seeds.txt ─▶ キーワード展開 ─▶ 記事生成 ─▶ 画像生成＋CTA ─▶ content/(JSON, 永続)
              (Claude/Ollama/テンプレ)                          │
                                                                ▼
                                              docs/(HTML+SVG, contentから再生成)
```

## 3つの動作モード（環境変数 `KOKI_LLM` で切替）

| モード | 条件 | 費用 | 中身 |
|------|------|------|------|
| **Claude** | `anthropic` ＋ `ANTHROPIC_API_KEY` | API課金 | 高品質なSEO記事 |
| **ローカルAI（Ollama）** | Ollama起動＋モデル取得 | **0円** | 自分のPCで生成・そこそこ品質 |
| **テンプレ** | 上記が無い場合 | **0円** | 構造化テンプレ（オフライン可・品質は低） |

既定の `auto` は「Claude → Ollama → テンプレ」の順に、使えるものを自動選択します。

## データの持ち方（積み上げの仕組み）

| 場所 | 役割 |
|------|------|
| `content/*.json` | 記事の**元データ（永続）**。実行のたびに新規記事だけ追記される |
| `docs/*.html` `docs/*.svg` | 公開用サイト。毎回 `content/` 全体から再生成される |

同じキーワードは二度生成しません（slug で判定）。だから毎日回しても重複せず積み上がります。

## 使い方

```bash
cd projects/koki-affiliate

# オフラインで動作確認（キー不要・積み上げ式）
PYTHONPATH=src python -m affiliate.cli run --seed "ロボット掃除機" --count 3 --out docs --content content

# シードをファイルから
PYTHONPATH=src python -m affiliate.cli run --seeds-file seeds.txt --count 5 --out docs --content content

# 保存済み記事からサイトだけ再ビルド
PYTHONPATH=src python -m affiliate.cli build --content content --out docs
```

`docs/index.html` をブラウザで開けば記事一覧が見られます。

## 完全無料で生成（ローカルAI / Ollama）

**API課金ゼロ**。自分のPC上で生成します。

```bash
# 1) Ollama を入れてモデルを取得（初回のみ） https://ollama.com
ollama pull llama3.1            # 日本語重視なら qwen2.5 などもおすすめ

# 2) ローカルAIで生成（キー不要）
KOKI_LLM=ollama affiliate run --seeds-file seeds.txt --count 3 --config config.toml
```

- `OLLAMA_MODEL`（既定 `llama3.1`）でモデル変更、`OLLAMA_HOST`（既定 `http://localhost:11434`）でリモート指定。
- 完全無料の自動運用は「**自分のPC/サーバーで cron**」が向きます（Actionsの無料枠だと重い）。

## 本番（Claudeで生成・最高品質）

```bash
pip install -e ".[llm]"
export ANTHROPIC_API_KEY=sk-ant-...
cp config.example.toml config.toml          # amazon_tag / site_url などを編集
affiliate run --seeds-file seeds.txt --count 5 --config config.toml
```

> Claude生成・Ollama生成の両経路は `tests/test_llm.py` でモック検証済みです。

## アイキャッチ画像

各記事に **1200×630 のアイキャッチSVGを自動生成**します（`images.py`）。外部サービス・APIキー
不要、著作権の心配なし、完全無料。OGP画像（`og:image`）とトップのカード画像にも使われます。

> ⚠️ Amazon等の**商品写真を直接貼るのは規約違反**になりがちです（公式は専用APIが必要）。
> 本ツールは安全な自動生成アイキャッチで代替しています。

## アフィリエイト登録（最初の1回だけ・手動）

ASPへの登録は本人確認・口座が必須で**自動化できません**（規約でも禁止）。おすすめ順や必要物は
**[ASP_GUIDE.md](ASP_GUIDE.md)** にまとめました。登録後はタグを `config.toml` に入れるだけで、
**既存記事を含む全記事に自動反映**されます（CTAは表示時に差し込む設計）。

## 永遠に自動で公開する（GitHub Actions・Claude/Haiku向け）

`/.github/workflows/affiliate-daily.yml` が毎朝（07:00 JST）記事生成 → `content/` 追記コミット
→ GitHub Pages 公開を行います。

1. Settings → Secrets → `ANTHROPIC_API_KEY`（任意で Variables に `SITE_URL` / `AMAZON_TAG`）
2. Settings → **Pages** → Source = **GitHub Actions**
3. ワークフローをデフォルトブランチ（main）へ。手動実行は Actions タブ → **Run workflow**。

> 完全無料（Ollama）で回す場合は Actions ではなく、下記の cron をローカルで使ってください。

## 自前サーバー / 自分のPCで回す（cron・Ollamaにも対応）

```bash
0 7 * * * cd /path/koki-affiliate && KOKI_LLM=ollama \
  python -m affiliate.cli run --seeds-file seeds.txt --count 3 --config config.toml \
  && git add content docs && git commit -m "auto update" && git push
```

## ⚠️ 量産する前に知っておくこと（正直な注意）

- **「記事数 = 収益」ではありません。** Google は中身の薄い自動生成サイトをスパム評価で
  圏外に飛ばします。**量産だけのサイトはむしろ飛ばされる側**です。
- 勝ち筋は **ニッチ特化 ×（生成は自動・公開前に独自情報や一次データを足す）半自動**。
- ステマ規制対応の「PR / 広告」表記・`rel="nofollow sponsored"`・開示文は**消さないでください**。

## 構成

```
src/affiliate/
  config.py     設定（TOML, stdlibのみ）
  llm.py        生成バックエンド（Claude / Ollama / なし）の切替
  keywords.py   シード→ロングテール展開
  generate.py   記事生成（LLM/テンプレ）＋ slug
  affiliate.py  アフィリリンク組み立て＋CTA差し込み（表示時注入）
  images.py     アイキャッチSVGの自動生成（無料・依存ゼロ）
  markdown.py   依存ゼロの Markdown→HTML
  store.py      記事の永続化（content/*.json）
  render.py     静的サイト出力（index/記事/画像/css/sitemap/robots）
  pipeline.py   オーケストレーション（run=積み上げ / build=再生成）
  cli.py        CLI（run / build / keywords）
tests/          unittest（38件・標準ライブラリのみで実行可）
```

## テスト

```bash
PYTHONPATH=src python -m unittest discover -s tests -p "test_*.py"
```

## 次の一手（ロードマップ）

- WordPress / microCMS への自動投稿（REST API）
- 検索順位トラッキングと、伸びない記事の自動リライト
- 一次情報（価格API・スペック表・自前レビュー）の取り込みで独自性を担保
