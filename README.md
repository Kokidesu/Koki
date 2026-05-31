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
- 🤖 **Autonomous execution** — runs shell commands, edits files, verifies results.
- 🌐 **Bilingual** — replies in Japanese or English, matching your input automatically.
- 💻 **CLI-first** — `koki chat`, `koki ask "…"`, `koki task …`.

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

# Direct task DB ops (no LLM)
koki task add "ログイン機能を実装する" -p high --tags backend,auth
koki task list
koki task show 1
koki task done 1
koki task rm 1
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
  db.py      SQLite task store
  tools.py   Tool schemas + dispatch (task CRUD, shell, file IO)
  agent.py   Claude tool-use loop
  i18n.py    Bilingual message table
  cli.py     Command-line interface
```
