#!/bin/bash
# sync-rag.sh — Sync RAG Corpus dari Mac → ROG via Tailscale
# Jalankan: bash sync-rag.sh
#
# Opsi:
#   bash sync-rag.sh --build     # sync + rebuild vector DB di ROG
#   bash sync-rag.sh --cron      # mode cron (minimal log)

set -e

CORPUS_SOURCE="/Users/muhdansyarovy/Library/CloudStorage/OneDrive-Personal/10. Library/000. RAG Corpus"
CORPUS_DEST="rog:~/RAG Corpus/"
PROJECT_PATH="/Users/muhdansyarovy/Library/CloudStorage/OneDrive-Personal/06. Arsip/14. APP_DEV/11. RAG DeepSeek Sawit"
LOG_FILE="$HOME/.local/share/rag-sync.log"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
MODE="${1:-normal}"

mkdir -p "$(dirname "$LOG_FILE")"

# Mode cron: redirect semua output ke log
if [ "$MODE" = "--cron" ]; then
  exec >> "$LOG_FILE" 2>&1
  echo "[$TIMESTAMP] === SYNC RAG CORPUS (cron) ==="
else
  echo "[$TIMESTAMP] === SYNC RAG CORPUS ===" | tee -a "$LOG_FILE"
fi

# 1. Rsync corpus
echo "[$TIMESTAMP] 📤 Transfer ke ROG..."
if rsync -avz --delete \
  "$CORPUS_SOURCE/" \
  "$CORPUS_DEST" \
  --exclude=".DS_Store" \
  --exclude="sync-rag.sh" \
  >> "$LOG_FILE" 2>&1; then
  echo "[$TIMESTAMP] ✅ Sync selesai"
else
  echo "[$TIMESTAMP] ❌ Sync gagal!"
  exit 1
fi

# 2. Hitung file di kedua sisi
MAC_COUNT=$(find "$CORPUS_SOURCE" -type f -name "*.md" | wc -l)
ROG_COUNT=$(ssh rog 'find ~/RAG\ Corpus -type f -name "*.md" 2>/dev/null | wc -l')
echo "[$TIMESTAMP] 📊 Mac: $MAC_COUNT file | ROG: $ROG_COUNT file"

# 3. Sync project code ke ROG (exclude heavy dirs)
echo "[$TIMESTAMP] 📄 Sync project code..."
rsync -avz "$PROJECT_PATH/" rog:~/app-dev/11.\ RAG\ DeepSeek\ Sawit/ \
  --exclude="venv" --exclude="db" --exclude="knowledge" --exclude="__pycache__" \
  --exclude=".git" \
  >> "$LOG_FILE" 2>&1

# 4. Opsional: rebuild vector DB di ROG (pakai venv explicit)
if [ "$MODE" = "--build" ]; then
  echo "[$TIMESTAMP] 🔨 Rebuild vector DB di ROG..."
  ssh rog "cd ~/app-dev/11.\ RAG\ DeepSeek\ Sawit && rm -rf db/* && ./venv/bin/python3 bulk-import.py ~/RAG\ Corpus/" 2>&1 >> "$LOG_FILE"
  echo "[$TIMESTAMP] ✅ Vector DB rebuilt"
fi

echo "[$TIMESTAMP] ✅ Selesai"
echo "" >> "$LOG_FILE"
