# note 自動投稿キット（Gemini生成 → 自動投稿）

note の記事を **Geminiで自動生成**（本文＋サムネ画像）して、**note に自動投稿**するための一式です。
GitHub Actions に載せれば **あなたのPCを開いていなくても** クラウド上で毎日動きます。

対象アカウント: <https://note.com/light_roses761>

---

## 🔧 これは何をする？

1. `config.yaml` のテーマに沿って、Gemini が長文記事を生成（目標文字数は設定可能）
2. Gemini(Imagen) でサムネ画像を生成
3. ログイン済みブラウザを裏で動かして note に投稿（公開 or 下書き）
4. これを GitHub Actions が **1日3回**（09:00 / 13:00 / 19:00 JST）自動実行

---

## ⚠ 先に知っておいてほしいこと（正直な注意）

- **note には公式の投稿APIがありません。** だから「ログイン済みブラウザを自動操作」する方式です。
  - そのため、ログインの**セッション(cookie)を1回手動で取り出して**渡す必要があります（パスワードはコードにもクラウドにも保存しません）。
  - セッションは**時々切れる**ので、切れたら取り直してSecretをUpdateしてください。
- **AI記事を1日3本×2万文字で“即公開”は、note規約・スパム判定的にアカウント凍結リスクがあります。**
  最初は `config.yaml` で **`publish: false`（下書き）／本数や文字数を控えめ** にして、様子を見るのを強く推奨します。
- 投稿UIのセレクタは、note にアクセスできない環境で書いたため**ベストエフォート**です。
  UIがズレて失敗する場合は `playwright codegen https://note.com/notes/new` で実際の画面を見て微調整してください
  （ここはローカルのClaude Codeに「note投稿のセレクタを直して」と頼むと早いです）。

---

## ✅ PCを開いてなくても動かす（推奨：GitHub Actions）

### 1. Gemini APIキーを取る
<https://aistudio.google.com/apikey> でキーを発行。

### 2. note のログインセッションを取り出す（自分のPCで1回だけ）
```bash
cd projects/note-auto-poster
pip install -r requirements.txt
python -m playwright install chromium
python tools/export_note_session.py    # 開いた画面でnoteにログイン → Enter
```
→ `storage_state.json` ができます。

### 3. GitHub に Secret を2つ登録
リポジトリ → **Settings → Secrets and variables → Actions → New repository secret**
| 名前 | 中身 |
|------|------|
| `GEMINI_API_KEY` | 1.で取得したキー |
| `NOTE_STORAGE_STATE` | `storage_state.json` の中身を**まるごとコピペ** |

### 4. テーマを設定してコミット
`config.yaml` の `theme:` を自分のアカウントのテーマに書き換えて push。

### 5. 動かす
`.github/workflows/note-daily.yml` が毎日3回自動実行します。
Actions タブの **Run workflow** ボタンで手動テストも可能。

これで **PCを閉じていても** クラウド側で生成＆投稿が回ります。

---

## 💻 自分のPCで動かす場合（PCは起動が必要）

```bash
cd projects/note-auto-poster
pip install -r requirements.txt
python -m playwright install chromium
cp .env.example .env          # GEMINI_API_KEY を書く
export $(cat .env | xargs)
python tools/export_note_session.py   # 初回だけ
python run_daily.py                    # 生成→投稿
```
毎日動かすなら cron(mac/Linux) や タスクスケジューラ(Windows) に `run_daily.py` を登録。
※この方式は**実行時刻にPCが起動＆スリープ解除**している必要があります。

---

## ⚙ 設定（config.yaml）

| 項目 | 意味 |
|------|------|
| `theme` | 記事のテーマ（**必須・書き換える**） |
| `articles_per_run` | 1回の実行で作る本数（既定1） |
| `target_chars` | 1記事の目標文字数（既定20000。最初は3000〜推奨） |
| `publish` | `true`=公開 / `false`=下書き（**最初はfalse推奨**） |
| `tags` | ハッシュタグ |
| `text_model` / `image_model` | 使うGeminiモデル |
| `thumbnail` | サムネを作るか |

---

## ファイル構成
```
projects/note-auto-poster/
├─ config.yaml                 設定
├─ generate.py                 Geminiで本文＋サムネ生成
├─ post_note.py                Playwrightでnoteへ投稿
├─ run_daily.py                生成→投稿の一括実行（Actionsが呼ぶ）
├─ tools/export_note_session.py  ログインセッション取り出し（手元PCで1回）
├─ requirements.txt
└─ .github/workflows/note-daily.yml   1日3回の自動実行（リポジトリ直下）
```

> このキットは note / Gemini にアクセスできない隔離環境で作成したため、**未実行（動作未検証）**です。
> 最初の1回はローカルで `python run_daily.py` を試し、投稿UIのセレクタだけ実機で詰めてください。
