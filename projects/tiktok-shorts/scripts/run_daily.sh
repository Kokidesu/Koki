#!/usr/bin/env bash
# 毎日まとめて生成（→設定に従い下書き投稿）するためのラッパ。
# 使い方: scripts/run_daily.sh [本数]   例: scripts/run_daily.sh 10
set -euo pipefail

cd "$(dirname "$0")/.."

# .env を読み込む（ANTHROPIC_API_KEY / TIKTOK_* など）
if [ -f .env ]; then
  set -a; . ./.env; set +a
fi

export PYTHONPATH=src
N="${1:-10}"
mkdir -p logs
ts="$(date +%Y%m%d_%H%M%S)"

echo "[$(date '+%F %T')] start: run -n $N" | tee -a logs/daily.log
if python3 -m shorts run -n "$N" >>"logs/run_${ts}.log" 2>&1; then
  echo "[$(date '+%F %T')] done (logs/run_${ts}.log)" | tee -a logs/daily.log
else
  echo "[$(date '+%F %T')] FAILED (logs/run_${ts}.log)" | tee -a logs/daily.log
  exit 1
fi
