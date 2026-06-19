# Changelog — OPIN / RAG DeepSeek Sawit

Semua perubahan signifikan dicatat di sini.

Format: `YYYY-MM-DD` — versi — deskripsi

---

## 2026-06-20 — v2.0.0 — Fase 1 Selesai + Clean Corpus

### Added
- OPIN chatbot UI (`static/index.html`) — dark mode, responsive, suggestion chips, copy button
- `FASE-1.md` — dokumentasi detail Fase 1
- `ROADMAP.md` — roadmap 5 fase lengkap (RAG → benchmark → dataset → fine-tune → produk)
- `CHANGELOG.md` — file ini
- `Non Sawit/` folder — 16 file non-sawit dipisah dari corpus

### Changed
- **README.md** — rewrite total dengan arsitektur, alur, tech stack, biaya, konteks untuk AI lain
- `server.py` — ganti parser stdout → return object langsung, tambah `/` route untuk UI
- `rag.py` — ganti `opencode-batch` subprocess → `openai` SDK ke `api.deepseek.com/v1`
- `rag.py` — hapus `AVAILABLE_MODELS` (opencode), `subprocess`, `OPCODE_BATCH`
- `rag.py` — `ask()` return tuple `(answer, sources)` bukan print ke stdout
- `bulk-import.py` — skip folder `Non Sawit/` dan file `._` (macOS resource fork)
- `sync-rag.sh` — exclude `Non Sawit/` saat sync
- `server.py` — hapus `StaticFiles` mount, ganti `FileResponse` untuk `/`
- `requirements.txt` — tambah `openai`, `python-dotenv`
- `.gitignore` — tambah `.env`
- `.env` — file baru untuk API key

### Fixed
- systemd service path (spaces in directory name) — pakai wrapper script
- Static mount override API routes
- server restart via systemd

### Removed
- `opencode-batch` subprocess dependency
- `AVAILABLE_MODELS` (deepseek-v4-flash-free, big-pickle, dll)
- `OPCODE_BATCH` constant
- `--model`, `--list-models` CLI arguments
- 16 file non-sawit dari corpus (KBBI, maize, citrus, animal breeding, SAS docs, dictionaries)

---

## 2026-06-19 — v1.1.0 — Sync + Systemd + GitHub

### Added
- `sync-rag.sh` — rsync script Mac → ROG (--build, --cron mode)
- `rag-sawit.service` — systemd unit file untuk auto-start server
- `start-server.sh` — wrapper script (atasi spasi di path)
- `.gitignore`
- GitHub repo: `github.com/muhdansyarovy/rag-deepseek-sawit`
- launchd plist `com.muhdan.sync-rag` (auto-sync tiap jam)
- `bulk-import.py` — batch import semua .md ke ChromaDB

### Changed
- Sync corpus (5.755 file) dari Mac ke ROG via rsync + Tailscale
- Refactor `rag.py` — gunakan `chromadb.utils.embedding_functions.DefaultEmbeddingFunction` gantikan `sentence_transformers.SentenceTransformer`
- Hapus dependensi PyTorch/sentence-transformers
- Pakai ONNX `all-MiniLM-L6-v2` via ChromaDB bawaan

### Added (infrastructure)
- Python venv di ROG (`venv/`)
- chromadb, fastapi, uvicorn, python-multipart terinstall
- ROG corpus path: `~/RAG Corpus/`
- ROG project path: `~/app-dev/11. RAG DeepSeek Sawit/`
- Tailscale direct connection Mac ↔ ROG established

### Known
- Bulk import masih berjalan di tmux `rag-import` (5741 file)
- Biaya DeepSeek API: ~$1-2/bln untuk 100 query/hari

---

## 2026-06-10 — v1.0.0 — Initial Release

### Added
- `rag.py` — RAG engine dengan ChromaDB + sentence-transformers
- `server.py` — FastAPI server endpoint `/ask`, `/knowledge`, `/health`, `/stats`, `/models`
- `add-knowledge.py` — CLI add 1 file
- `requirements.txt` — chromadb, fastapi, uvicorn, python-multipart
- `README.md` — dokumentasi awal
- `RENCANA.md` — rencana proyek awal

### Architecture (v1.0.0)
- LLM: `opencode-batch` (deepseek-v4-flash-free)
- Embedding: `sentence_transformers.SentenceTransformer('all-MiniLM-L6-v2')`
- Vector DB: ChromaDB
- Chunk: 500 chars, overlap 50
- DB path: `db/`
- 5 model LLM tersedia via opencode-batch

---

## Key Decisions History

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-06-20 | Ganti opencode-batch → DeepSeek API | Subprocess unreliable, API persistent, bisa scale |
| 2026-06-20 | Pisah 16 file non-sawit ke Non Sawit/ | KBBI dll mengganggu retrieval quality |
| 2026-06-19 | Pakai ONNX → DefaultEmbeddingFunction | Hindari PyTorch (2GB), cukup ONNX (79MB) |
| 2026-06-19 | ROG sebagai server 24/7 via Tailscale | Gratis, selalu online |
| 2026-06-10 | RAG + Local Embed + External LLM | Cepat deliver, tanpa GPU |
