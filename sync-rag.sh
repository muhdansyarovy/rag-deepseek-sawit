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
LOG_FILE="$HOME/.local/share/rag-sync.log"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
MODE="${1:-normal}"

mkdir -p "$(dirname "$LOG_FILE")"

echo "[$TIMESTAMP] === SYNC RAG CORPUS ===" | tee -a "$LOG_FILE"

# 1. Rsync
echo "[$TIMESTAMP] 📤 Transfer ke ROG..." | tee -a "$LOG_FILE"
if rsync -avz --delete \
  "$CORPUS_SOURCE/" \
  "$CORPUS_DEST" \
  --exclude=".DS_Store" \
  --exclude="sync-rag.sh" \
  >> "$LOG_FILE" 2>&1; then
  echo "[$TIMESTAMP] ✅ Sync selesai" | tee -a "$LOG_FILE"
else
  echo "[$TIMESTAMP] ❌ Sync gagal!" | tee -a "$LOG_FILE"
  exit 1
fi

# 2. Hitung file di kedua sisi
MAC_COUNT=$(find "$CORPUS_SOURCE" -type f -name "*.md" | wc -l)
ROG_COUNT=$(ssh rog 'find ~/RAG\ Corpus -type f -name "*.md" 2>/dev/null | wc -l')
echo "[$TIMESTAMP] 📊 Mac: $MAC_COUNT file | ROG: $ROG_COUNT file" | tee -a "$LOG_FILE"

# 3. Opsional: rebuild vector DB di ROG
if [ "$MODE" = "--build" ]; then
  echo "[$TIMESTAMP] 🔨 Rebuild vector DB di ROG..." | tee -a "$LOG_FILE"
  ssh rog "cd ~/app-dev/11.\ RAG\ DeepSeek\ Sawit && rm -rf db/* && python3 add-knowledge.py --add-all ~/RAG\ Corpus/" 2>&1 | tee -a "$LOG_FILE"
  echo "[$TIMESTAMP] ✅ Vector DB rebuilt" | tee -a "$LOG_FILE"
fi

echo "[$TIMESTAMP] ✅ Selesai" | tee -a "$LOG_FILE"
echo "" >> "$LOG_FILE"
