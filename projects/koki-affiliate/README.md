# koki-affiliate — 全自動アフィリエイト記事ジェネレーター

シードキーワードを1つ渡すと、**キーワード展開 → 記事生成 → アフィリリンク差し込み → 静的サイト出力**
までを1コマンドで全自動実行する MVP です。出力はそのまま GitHub Pages に乗せて公開できます。

```
シード語 ──▶ キーワード展開 ──▶ 記事生成 ──▶ アフィリCTA差し込み ──▶ 静的サイト(out/)
            (Claude/fallback)   (Claude/fallback)
```

## 2つの動作モード

| モード | 条件 | 中身 |
|------|------|------|
| **Claude（本番）** | `anthropic` 導入 ＋ `ANTHROPIC_API_KEY` 設定 | Claude が本物のSEO記事を生成 |
| **テンプレ（fallback）** | 上記が無い場合 | 構造化テンプレで記事を生成（**完全オフラインで動く**） |

まず fallback でパイプラインの動きを体感 → APIキーを入れて本番に切り替え、という流れで使えます。

## 使い方

```bash
cd projects/koki-affiliate

# 1) オフラインで動作確認（キー不要）
PYTHONPATH=src python -m affiliate.cli run --seed "ロボット掃除機" --count 3 --out out

# 2) 本番（Claudeで生成）
pip install -e ".[llm]"
export ANTHROPIC_API_KEY=sk-ant-...
affiliate run --seed "ロボット掃除機" --count 5 --config config.toml

# キーワードだけ見たいとき
affiliate keywords --seed "ロボット掃除機" --count 10
```

生成後、`out/index.html` をブラウザで開けば記事一覧が見られます。

## 「永遠に自動で量産」する（cron）

```bash
# 毎朝7時に5記事追記してGitHub Pagesへ公開（例）
0 7 * * * cd /path/koki-affiliate && PYTHONPATH=src ANTHROPIC_API_KEY=sk-ant-... \
  python -m affiliate.cli run --seed "ロボット掃除機" --count 5 --config config.toml \
  && cd out && git add -A && git commit -m "auto update" && git push
```

## GitHub Pages で公開

1. `base_dir` を `docs` にして出力（または `out/` を `gh-pages` ブランチへ push）。
2. リポジトリの Settings → Pages で公開元ブランチ/フォルダを指定。
3. `site_url` を実際の公開URLに合わせると、`canonical` と `sitemap.xml` が正しくなります。

## ⚠️ 量産する前に知っておくこと（正直な注意）

- **「記事数 = 収益」ではありません。** Google は中身の薄い自動生成サイトをスパム評価で
  圏外に飛ばしています。**量産だけのサイトはむしろ飛ばされる側**です。
- 勝ち筋は **ニッチ特化 ×（生成は自動・公開前に独自情報や一次データを足す）半自動**。
  本ツールはその土台（生成の自動化）であって、独自性は人が乗せる前提です。
- **ステマ規制（2023.10〜）対応**として、CTAには「PR / 広告」表記、リンクには
  `rel="nofollow sponsored"`、フッターにアフィリエイト開示文を入れています。
  公開時はこの表示を消さないでください。
- Amazonアソシエイト等、各ASPの規約（虚偽の体験談・価格の固定表記の禁止など）も必ず確認を。

## 構成

```
src/affiliate/
  config.py     設定（TOML, stdlibのみ）
  llm.py        Claude呼び出し（無ければfallback）
  keywords.py   シード→ロングテール展開
  generate.py   記事生成（Claude/テンプレ）＋ slug
  affiliate.py  アフィリリンク組み立て＋CTA差し込み
  markdown.py   依存ゼロの Markdown→HTML
  render.py     静的サイト出力（index/記事/css/sitemap/robots）
  pipeline.py   オーケストレーション
  cli.py        CLI（run / keywords）
tests/          unittest（標準ライブラリのみで実行可）
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
