# DeepSeek Sawit — RAG API

RAG khusus sawit, gratis, bisa dipanggil dari OpenWA / Linux / mana aja.

## Arsitektur

```
OpenWA ---- HTTP ----> deepseek-sawit API ---->
  (tanya)              │                        ├── ChromaDB (vector dokumen sawit)
                       │                        └── DeepSeek V4 Flash (via opencode-batch)
                       └──> Balik jawaban ke OpenWA
```

## Stack (GRATIS semua)

| Komponen | Tool | Biaya |
|----------|------|-------|
| LLM | DeepSeek V4 Flash (via OpenCode) | ✅ Gratis |
| Embedding | sentence-transformers `all-MiniLM-L6-v2` | ✅ Gratis |
| Vector DB | ChromaDB | ✅ Gratis |
| API Server | FastAPI + uvicorn | ✅ Gratis |
| Hosting | Laptop/Server Linux mana aja | ✅ Gratis |

## Struktur Folder (nanti)

```
rag-deepseek-sawit/
├── server.py              ← API endpoint FastAPI
├── rag.py                 ← RAG engine (embed + retrieve + generate)
├── add-knowledge.py       ← CLI masukin dokumen ke ChromaDB
├── requirements.txt       ← dependensi
├── knowledge/             ← simpan dokumen sawit (PDF/txt)
├── db/                    ← folder ChromaDB (auto-generated)
└── README.md
```

## Cara Kerja

1. **Masukin dokumen:** `python add-knowledge.py knowledge/laporan.txt`
   → Dokumen dipecah (chunking) → di-embedding → disimpan di ChromaDB

2. **Tanya:** `POST /ask` dengan `{"question": "..."}`
   → Cari 3-5 chunk paling relevan di ChromaDB
   → Gabungin jadi prompt + konteks
   → Kirim ke DeepSeek V4 Flash via `opencode-batch`
   → Balik jawaban

3. **Integrasi OpenWA:** tinggal call endpoint API dari OpenWA webhook

## API Endpoint (nanti)

```
POST /ask
Body: {"question": "berapa jarak tanam sawit?"}
Response: {"answer": "...", "sources": ["dokumen1.pdf", ...]}

POST /knowledge
Body: (file upload) → masukin dokumen baru

GET /health
Response: {"status": "ok", "chunks": 1234}
```

## Catatan

- Pakai DeepSeek V4 Flash via `opencode-batch` — response 2-5 detik
- Embedding lokal, gak perlu API key
- Bisa jalan di Linux tanpa GPU (CPU aja cukup)
- Semua komponen open source

---

*Direncanakan: implementasi setelah installasi Linux selesai.*
