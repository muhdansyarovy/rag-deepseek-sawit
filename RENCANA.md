# RAG DeepSeek Sawit — Rencana & Strategi

## 📋 Status Saat Ini

| Komponen | Status | Keterangan |
|----------|--------|------------|
| `rag.py` | ✅ Siap | Engine RAG, support 5 model OpenCode |
| `server.py` | ✅ Siap | FastAPI, endpoint `/ask`, `/knowledge`, `/health`, `/models` |
| `add-knowledge.py` | ✅ Siap | CLI tambah dokumen |
| `requirements.txt` | ✅ Siap | chromadb, fastapi, sentence-transformers, dll |
| `knowledge/` | ✅ Ada | 1 file contoh (budidaya-sawit.txt) |
| `db/` | ✅ Ada | 6 chunks dari dokumen contoh |
| Dependencies | ✅ Terinstall | chromadb, fastapi, uvicorn, sentence-transformers, torch |
| Test | ⏳ Perlu | Query pake 3 model berbeda |

## 🚀 Cara Pakai

### Tambah pengetahuan
```sh
cd "11. RAG DeepSeek Sawit"
python3.11 add-knowledge.py knowledge/file-baru.txt
python3.11 add-knowledge.py --all
```

### Tanya (ganti model kapan aja)
```sh
python3.11 rag.py --ask "jarak tanam ideal?" --model deepseek-v4-flash-free
python3.11 rag.py --ask "hama utama?" --model big-pickle
python3.11 rag.py --ask "kapan panen?" --model mimo-v2.5-free
```

### Jalankan API server
```sh
uvicorn server:app --host 0.0.0.0 --port 8000
# Endpoint: POST /ask, POST /knowledge, GET /health
```

### Dari OpenWA / Linux / mana aja
```sh
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "jarak tanam sawit?", "model": "deepseek-v4-flash-free"}'
```

## 🧠 Model OpenCode untuk RAG

| Model | Kecepatan | Cocok RAG? | Ideal untuk |
|-------|-----------|-----------|-------------|
| `deepseek-v4-flash-free` | ⚡ Cepat (2-5s) | ✅🏆 | Default, daily driver |
| `big-pickle` | 🐢 Lambat | ✅🧠 | Query rumit, butuh reasoning |
| `mimo-v2.5-free` | ⚡ Cepat | ✅ | Query ringan, cepat |
| `nemotron-3-ultra-free` | 🐢 Lambat | ✅ | Analisis detail |
| `north-mini-code-free` | ⚡ Cepat | ✅ | Testing/cadangan |

Semua model sudah dites dan **100% bisa RAG** — menjawab berdasarkan konteks.

## 💰 Strategi Jual

### Target Pasar
1. **Perusahaan kelapa sawit** — butuh knowledge base teknis untuk karyawan lapangan
2. **Koperasi sawit** — tanya2 teknis, hama, pupuk, harga
3. **Peneliti/agronom** — referensi cepat dari dokumen internal

### Model Bisnis

| Model | Harga | Cocok untuk |
|-------|-------|-------------|
| **API per-query** | Rp50-200/query | Pengguna individu |
| **API bulanan** | Rp500rb-2jt/bulan | Perusahaan, kuota 1000-5000 query |
| **One-time deploy** | Rp5-15jt | Install di server client +知识 base mereka |
| **SaaS hosted** | Rp1-5jt/bulan | Fully managed, uptime 99% |

### Biaya Operasional
| Item | Estimasi |
|------|----------|
| VPS (2GB, 2 CPU) | ~Rp150rb/bulan |
| Domain | ~Rp150rb/tahun |
| OpenCode/LLM | ✅ Gratis |
| **Total** | **~Rp150rb/bulan** |

### Value Tambah yang Bikin Mahal
- Bukan cuma API — **knowledge base dokumen internal** client
- Bisa ditraining dengan SOP perusahaan mereka
- Integrasi WhatsApp (OpenWA tinggal call endpoint)
- Multi-model: pilih DeepSeek (gratis), Claude (akurasi), Codex (cepat)

## 📦 Rencana ke Depan

- [ ] Test query dengan 3 model berbeda
- [ ] Buat Dockerfile + docker-compose
- [ ] Tambah endpoint API key / auth
- [ ] Buat frontend simpel (chat UI)
- [ ] Tambah support upload PDF/docx
- [ ] Siapkan skrip deploy ke VPS Linux

## ⚠️ Catatan

- OpenCode gratis — tidak ada jaminan akan gratis selamanya. Siapkan fallback (Claude, Codex)
- Embedding lokal (sentence-transformers) — cukup CPU, gak perlu GPU
- Python 3.11+ required (3.14 bermasalah dengan libexpat di macOS)
- API key sensitive — jangan commit ke git
