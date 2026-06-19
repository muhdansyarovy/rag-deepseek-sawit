# OPIN — Sawit AI RAG Engine

RAG engine spesifik budidaya kelapa sawit. Corpus 5.741 dokumen teknis dari PPKS, buku referensi, jurnal, dan disertasi. Ditenagai ChromaDB (vector search) + DeepSeek API (LLM).

---

## Arsitektur

```
┌──────────────────────────────────────────────────────────────┐
│                          USER                                 │
│   Browser (OPIN UI)  │  curl  │  App  │  WhatsApp            │
└──────────────────────┬───────────────────────────────────────┘
                       │ HTTP
                       ▼
┌──────────────────────────────────────────────────────────────┐
│              FastAPI Server (ROG :8000)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐ │
│  │ OPIN UI  │  │  /ask    │  │ /health  │  │  /knowledge  │ │
│  │ index.html│ │ endpoint │  │ endpoint │  │  endpoint    │ │
│  └──────────┘  └────┬─────┘  └──────────┘  └──────────────┘ │
│                     │                                        │
└─────────────────────┬────────────────────────────────────────┘
                      │
         ┌────────────┼────────────┐
         ▼            ▼            ▼
┌────────────┐ ┌──────────┐ ┌──────────┐
│  ChromaDB  │ │  DeepSeek │ │ ONNX     │
│ vector DB  │ │  API      │ │ Embed    │
│ (db/)      │ │ (remote)  │ │ (lokal)  │
└────────────┘ └──────────┘ └──────────┘
     │              │
     │ retrieve     │ generate
     ▼              ▼
┌────────────────────────────────────┐
│       5.741 file .md corpus        │
│  (folder: ~/RAG Corpus/)           │
└────────────────────────────────────┘
```

## Alur Query

```
User: "Apa dosis pupuk NPK untuk TBM 1?"
        │
        ▼
  1. OPIN UI → POST /ask {"question": "..."}
        │
        ▼
  2. ChromaDB query (cosine similarity)
     - Embed question via ONNX (all-MiniLM-L6-v2)
     - Cari 3 chunk terdekat dari 200k+ chunks
        │
        ▼
  3. Prompt builder
     System: "Anda asisten ahli sawit..."
     User: "KONTEKS: [3 chunk teratas] PERTANYAAN: ..."
        │
        ▼
  4. POST ke api.deepseek.com/v1/chat/completions
     Model: deepseek-chat
        │
        ▼
  5. Response → OPIN UI → User lihat jawaban + sumber
```

---

## Technology Stack

| Layer | Teknologi | Detail |
|-------|-----------|--------|
| **LLM** | DeepSeek API (`deepseek-chat`) | via `openai` SDK ke `api.deepseek.com/v1` |
| **Vector DB** | ChromaDB + HNSW (cosine) | PersistentClient, `all-MiniLM-L6-v2` via DefaultEmbeddingFunction |
| **Embedding** | ONNX Runtime (`all-MiniLM-L6-v2`) | 384-dim vectors, ~79MB model, CPU-only, tanpa PyTorch |
| **API Server** | FastAPI + Uvicorn | systemd service, auto-restart |
| **Frontend** | Vanilla HTML/CSS/JS | OPIN chatbot, dark mode, responsive |
| **Hosting** | ROG laptop (Linux Mint) | Tailscale VPN, IP: 100.116.15.57:8000 |
| **Sync** | rsync + launchd (Mac → ROG) | Auto-sync tiap jam |
| **Version Control** | GitHub | `github.com/muhdansyarovy/rag-deepseek-sawit` |

### Biaya Operasional

| Komponen | Biaya/bln |
|----------|-----------|
| DeepSeek API (100 query/hari) | ~$1-2 |
| Hosting ROG | Rp 0 (existing) |
| **Total** | **~$1-2/bln** |

---

## File Structure

```
rag-deepseek-sawit/
├── README.md           ← Ini — dokumentasi utama
├── ROADMAP.md          ← Roadmap 5 fase (RAG → dataset → fine-tune → produk)
├── FASE-1.md           ← Detail eksekusi Fase 1 (RAG + DeepSeek API)
├── CHANGELOG.md        ← Riwayat perubahan versi
├── RENCANA.md          ← Rencana awal proyek (legacy)
│
├── server.py           ← FastAPI server (endpoint: /, /ask, /health, /stats, /models, /knowledge)
├── rag.py              ← RAG engine: chunking, embed, retrieve, generate (DeepSeek API)
├── bulk-import.py      ← Batch import semua .md dari folder ke ChromaDB (skip Non Sawit/)
├── add-knowledge.py    ← CLI import 1 file
├── sync-rag.sh         ← Script rsync corpus Mac → ROG
│
├── static/
│   └── index.html      ← OPIN chatbot UI
│
├── requirements.txt    ← Python dependencies
├── .env                ← DEEPSEEK_API_KEY (tidak di-track git)
├── .gitignore
│
├── rag-sawit.service   ← systemd unit file (server auto-start)
├── start-server.sh     ← Wrapper script untuk systemd
│
├── db/                 ← ChromaDB vector store (auto-generated)
├── knowledge/          ← Folder upload dokumen via API
├── Non Sawit/          ← File non-sawit yang dipisah (16 file)
```

---

## Cara Pakai

### API

```bash
# Query
curl -X POST http://100.116.15.57:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Apa dosis pupuk NPK untuk TBM 1?"}'

# Response
# {"answer":"...", "model":"deepseek-chat", "sources":["file1.md", "file2.md"]}

# Cek status
curl http://100.116.15.57:8000/health
# {"status":"ok", "chunks": 203891}

# Detail statistik
curl http://100.116.15.57:8000/stats
```

### UI

Buka browser: `http://100.116.15.57:8000`

### CLI (langsung di ROG)

```bash
ssh rog
cd ~/app-dev/11. RAG DeepSeek Sawit
./venv/bin/python3 rag.py --ask "Apa itu BJR?"
```

---

## Server Management

```bash
# Status server
ssh rog 'sudo systemctl status rag-sawit.service'

# Restart server
ssh rog 'sudo systemctl restart rag-sawit.service'

# Log server
ssh rog 'sudo journalctl -u rag-sawit.service -n 50'
```

---

## Konteks untuk AI Lain

Project ini dirancang agar bisa dilanjutkan oleh AI lain (atau developer lain) dengan membaca dokumentasi ini.

### Critical Context

| Item | Detail |
|------|--------|
| **Corpus** | 5.741 file .md di `~/RAG Corpus/` (ROG) |
| **ChromaDB** | 200k+ chunks di `~/app-dev/11. RAG DeepSeek Sawit/db/` |
| **API Key** | Di `.env` — `DEEPSEEK_API_KEY` |
| **Server** | ROG (Linux Mint), systemd service `rag-sawit.service` |
| **Network** | Tailscale IP: `100.116.15.57:8000` |
| **Import progress** | tmux session `rag-import` (cek: `tmux capture-pane -t rag-import -p -S -3`) |
| **Sync** | Mac → ROG via rsync, cron tiap jam via launchd (`com.muhdan.sync-rag`) |
| **Git** | `github.com/muhdansyarovy/rag-deepseek-sawit` |

### Next Steps (berdasarkan ROADMAP)

```
Fase 1: RAG + DeepSeek API     ✅ SELESAI
Fase 2: Benchmark model gratis  ⏳ BERIKUTNYA (Qwen 3.6 27B / local)
Fase 3: Dataset QA              ⏳ (bangun 10k-20k QA pairs)
Fase 4: Fine-tune               ⏳
Fase 5: Produk komersial        ⏳
```

### Arsitektur Keputusan (jika AI perlu melanjutkan)

1. **Kenapa DeepSeek API bukan local LLM?** — Biaya minimal $1-2/bln, kualitas tinggi, tanpa GPU
2. **Kenapa ONNX bukan PyTorch?** — ROG tanpa GPU, ONNX lebih ringan (79MB vs 2GB)
3. **Kenapa RAG bukan pure fine-tune?** — RAG memberikan akurasi fakta (dari dokumen), fine-tune untuk domain expertise
4. **Kenapa file dipisah Non Sawit/?** — 16 file dictionary/crops lain mengganggu retrieval quality
