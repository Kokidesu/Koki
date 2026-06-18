# 🩺 AI ドクター / AI Doctor

チャット形式で健康相談ができるWebアプリ。「世界トップクラスの医師AI・即答」をコンセプトに、
症状の説明 → 考えられる原因・対処法・受診の目安を、やさしく素早く返します。

- **チャット形式**（会話が続く・履歴はブラウザに保存）
- **使う人はAPIキー不要**（裏のCloudflare Workerが代わりにAIを動かす）
- 日本語 / English 切り替え、即答 / じっくり モード
- ストリーミング表示（少しずつ出てくる）
- スマホ対応・単一HTML

> ⚠️ **これは医療行為ではありません。** 一般的な健康情報を提供するAIで、医師の診断・治療の代わりにはなりません。
> 緊急時（胸の痛み・呼吸困難・意識障害・大量出血など）は、すぐに **119番（救急）** に連絡してください。

---

## 構成

| ファイル | 役割 |
|---|---|
| `index.html` | チャット画面（フロント）。`/api/chat` に投げて返事を受け取るだけ。 |
| `worker/` | Cloudflare Worker（バックエンド）。AIを実行し、ページも配信する。 |

裏でAIを動かすので、**使う友達はキーを一切入力しなくてOK**。あなた側でWorkerを一度デプロイするだけです。

AIの動力源は自動判定:
- `GEMINI_API_KEY` シークレットを設定 → **Google Gemini**（より高品質）
- 何も設定しない → **Cloudflare Workers AI**（別途のAPIキー不要・CF無料枠）

---

## デプロイ手順（おすすめ：これだけで「鍵なしの共有リンク」が完成）

必要なもの: 無料の [Cloudflare アカウント](https://dash.cloudflare.com/sign-up) と Node.js。

```bash
cd projects/ai-doctor/worker
npx wrangler login        # ブラウザでCloudflareにログイン
npx wrangler deploy       # デプロイ（index.html も一緒に配信される）
```

完了すると次のようなURLが出ます:

```
https://ai-doctor.<あなたのサブドメイン>.workers.dev
```

→ **このURLを友達に送るだけ。** キー入力なしでチャットできます。

> 初回だけ Workers AI の有効化を求められることがあります（ダッシュボードの指示に従えば無料で有効化できます）。

### （任意）Geminiでより高品質にする
Workers AIの代わりにGoogle Geminiを使いたい場合は、無料キーをシークレットとして登録するだけ:

```bash
npx wrangler secret put GEMINI_API_KEY   # https://aistudio.google.com/apikey で無料発行
```

登録するとWorkerが自動でGeminiを使います（友達側の操作は変わりません）。

---

## ローカルで試す

```bash
cd projects/ai-doctor/worker
npx wrangler dev
# 表示された http://localhost:8787 を開く
```

---

## GitHub Pages のまとめサイトにも載せる場合（任意）

このリポジトリの `kokidesu.github.io/koki/` にも `/ai-doctor/` として配信されます。
ただしPages版は `index.html` だけなので、AIに繋ぐには上でデプロイしたWorkerのURLを教える必要があります。次のどちらか:

- `index.html` 冒頭の `const BACKEND_URL = "";` に Worker のURLを入れてコミット（全員に有効）、または
- 画面の「設定 → 詳細設定」でWorkerのURLを保存（その端末のみ）。

一番手軽なのは、上のWorkerのURLをそのまま共有することです。

---

## メモ
- Windows で `wrangler deploy` の `[build]` が動かない場合は、`worker/site/` に `index.html` を手動コピーしてから実行してください。
- 会話履歴は端末のブラウザ（localStorage）にのみ保存されます。「＋ 新しい相談」で消去できます。
- モデルは `worker/worker.js` の `CF_MODEL` で変更できます。
