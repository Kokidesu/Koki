# ケース面接ドリル（全コンサル対応）

コンサルのケース面接対策が、スマホ1つでできる学習アプリ。
依存ライブラリなしの **`index.html` 1ファイル完結**（HTML/CSS/JS）。そのままブラウザで開くだけで動く。

## 中身

| セクション | 内容 |
|------|------|
| ホーム | ケース面接の全体像・評価ポイント・進め方 |
| ファーム別 | MBB（McK/BCG/Bain）＋ 戦略系・総合系 12+ ファームの「型」と対策 |
| フレームワーク | 収益性・市場参入・M&A・価格・コスト・成長・市場規模 など8つ |
| 練習ケース | タイプ別・ファーム別の8ケース（構造化→計算例→結論つき、解答は開閉式） |
| フェルミ推定 | 市場規模・個数の概算ドリル（推定例つき） |
| 暗算トレーナー | 60秒チャレンジ（やさしい〜ビジネス算の4難易度、自動生成） |
| 思考タイマー | 構造化60秒〜本番30分のプリセットタイマー |
| 用語集 | 頻出ワードを検索つきで |

## ローカルで見る

```bash
# どちらでもOK
open projects/case-interview/index.html
# or
cd projects/case-interview && python3 -m http.server 8000   # → http://localhost:8000
```

## 公開（友達に送るURL）

リポジトリの GitHub Pages で公開する。`.github/workflows/deploy-case-interview.yml` が
`main` への push 時に `projects/case-interview/` を自動デプロイする。

公開URL: **https://kokidesu.github.io/koki/**

> 内容は一般的なケース面接対策の学習用。各社の実際の選考内容を保証するものではありません。
