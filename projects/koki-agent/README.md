# Koki — 日英対応 課題管理＆実行エージェント

Koki (コウキ) is a bilingual (Japanese / English) AI agent that **manages your tasks
and actually executes them**. It keeps a local SQLite task database, and uses Claude
with tool-use to break down requests, run shell commands, read/write files, and log
its progress — all while replying in whatever language you wrote in.

Koki は、課題を**管理するだけでなく実行まで**行う日英バイリンガルの AI エージェントです。
ローカルの SQLite に課題を保存し、Claude のツール実行機能でコマンド実行・ファイル操作・
進捗ログ記録を自律的に行います。

## Features / 特徴

- 🗂 **Task DB** — add / list / update / log tasks with priority, tags and dependencies.
- 🧠 **ほのちゃん / Hono-chan** — `koki research "..."` asks a world-class research persona that searches the web, cross-checks sources, and answers with extreme specificity and citations. Uses the most capable model + extended thinking.
- 🧩 **Auto planning** — `koki plan "ゴール"` decomposes a goal into concrete tasks.
- 🤖 **Autonomous execution** — `koki run` works through tasks: runs shell, edits files, verifies, logs.
- 🔄 **GitHub sync** — import issues as tasks and push tasks back as issues.
- 🌐 **Bilingual** — replies in Japanese or English, matching your input automatically.
- 💻 **CLI-first** — `koki chat`, `koki ask`, `koki plan`, `koki run`, `koki gh`, `koki task`.

## Install / インストール

```bash
pip install -e .
export ANTHROPIC_API_KEY=sk-ant-...
```

## Usage / 使い方

```bash
# Interactive agent (manages + executes)
koki chat

# One-shot request
koki ask "READMEのtypoを直してテストを実行して"

# ほのちゃんに聞く — 何でも超具体的に、出典付きで調べて答える
koki research "2025年の日本の実質GDP成長率と、その主因を具体的に"
koki hono "光合成のカルビン回路を高校生にもわかるように、でも正確に"
# 賢さ最大化: 最上位モデルを指定（APIキーが対応している場合）
#   export KOKI_RESEARCH_MODEL=claude-opus-4-8

# Decompose a goal into tasks, then execute them autonomously
koki plan "TODOアプリのバックエンドAPIを作る"
koki run                      # work through all outstanding tasks
koki run --id 3               # work a single task

# GitHub Issues sync (needs GITHUB_TOKEN)
koki gh pull owner/repo       # import issues as tasks
koki gh push owner/repo 3     # create an issue from task #3

# Direct task DB ops (no LLM)
koki task add "ログイン機能を実装する" -p high --tags backend,auth
koki task list
koki task show 1
koki task done 1
koki task rm 1
```

## Tests / テスト

```bash
pip install pytest
PYTHONPATH=src pytest tests/ -q
```

## Configuration / 設定

| Env var | Meaning |
| --- | --- |
| `ANTHROPIC_API_KEY` | Required. Your Anthropic API key. |
| `KOKI_MODEL` | Model to use (default `claude-sonnet-4-6`). |
| `KOKI_DB` | Path to the SQLite DB (default `~/.koki/koki.db`). |
| `KOKI_LANG` | Force `ja` or `en` for CLI chrome (otherwise auto-detected). |

## Safety / 安全性

Shell execution is enabled by default in `chat`/`ask`. Pass `--no-shell` to disable it.
Koki is instructed to explain destructive commands before running them.

## Layout / 構成

```
src/koki/
  db.py           SQLite task store
  tools.py        Tool schemas + dispatch (task CRUD, shell, file IO)
  agent.py        Claude tool-use loop + plan() / run_tasks()
  github_sync.py  GitHub Issues <-> task sync (stdlib only)
  i18n.py         Bilingual message table
  cli.py          Command-line interface
tests/            pytest suite (db, tools, github sync)
```
