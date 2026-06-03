# note-bot（ローカル版・シンプル）

Gemini で記事（＋サムネ）を生成して note に自動投稿する、**Macで動かすだけ**の1ファイル版。
クラウドもCookieもSecretも使いません。

## つかいかた（3ステップ）

```bash
cd projects/note-bot
pip install -r requirements.txt
python -m playwright install chromium
export GEMINI_API_KEY=あなたのキー        # https://aistudio.google.com/apikey
python note_bot.py
```

- 初回は Chrome が開くので、**note にログイン**（Googleログインでお手元の認証もOK）→ ターミナルで Enter。
- 以降は `.note-profile/` にログインが保存され、**自動でログイン状態**になります。

## 設定（config.yaml）
| 項目 | 意味 |
|------|------|
| `theme` | `"auto"`=アカウントから自動推定 / 文字列で固定 |
| `target_chars` | 1記事の文字数（既定20000） |
| `publish` | `false`=下書き / `true`=公開（**まず false で1本確認**） |
| `loop` | `true`=PC起動中ずっと連続実行 |
| `interval_minutes` | 連続実行の間隔 |
| `max_per_day` | **1日の投稿上限（凍結対策・必ず付ける）** |
| `headless` | `false`=画面表示 / `true`=非表示 |

## PCが起きてる間ずっと回す
`config.yaml` で `loop: true` にして `python note_bot.py`。
`interval_minutes` ごとに実行し、`max_per_day` に達したら止まります（翌日リセット）。
※Macがスリープすると止まります。起こし続けたい時は別ターミナルで `caffeinate -i` 等。

## 注意（正直に）
- note には公式投稿APIが無いため、投稿は画面操作の自動化です。`note_bot.py` の投稿UIセレクタは
  実機未検証なので、ズレたら `playwright codegen https://note.com/notes/new` で直してください。
- **AI記事の大量・即公開はアカウント凍結リスク**があります。`max_per_day` は低めから。
