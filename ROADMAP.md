# Roadmap Sawit AI

## Visi
Membangun AI model spesifik budidaya kelapa sawit dan menjualnya sebagai produk.

---

## Fase 1 — RAG + DeepSeek API (1 minggu)

### Tujuan
Ganti `opencode-batch` (subprocess CLI) → DeepSeek API via HTTP. API langsung jalan 24/7 dengan biaya minimal.

### Perubahan Kode

| File | Perubahan |
|------|-----------|
| `rag.py` | Hapus `subprocess.run([OPCODE_BATCH, ...])` di fungsi `ask()`. Ganti dengan `openai` SDK call ke `https://api.deepseek.com/v1` |
| `server.py` | Sesuaikan parsing response dari format baru |
| `requirements.txt` | Tambah `openai`, `python-dotenv` |
| `.env` | Simpan `DEEPSEEK_API_KEY`, `DEEPSEEK_MODEL` |
| `.gitignore` | Tambah `.env` |

### Alur Setelah Fase 1

```
📄 5.755 file .md → ChromaDB (ONNX embed)
                         ↓
Pertanyaan → retrieve 3 chunk → prompt
                                   ↓
               🌐 api.deepseek.com/v1 (DeepSeek Chat)
                                   ↓
                              💬 Jawaban
```

### Biaya Operasional

| Item | Biaya |
|------|-------|
| DeepSeek API (10k query/bln) | ~$2-3 |
| Server ROG (listrik + internet) | Rp 0 (existing) |
| **Total** | **~Rp 30-45rb/bln** |

---

## Fase 2 — Benchmark Model Gratis (2-5 hari)

Setelah DeepSeek API stabil, uji coba model lokal gratis:

1. Install Ollama di ROG
2. Pull Qwen 3.6 27B (open weights, BI native)
3. Test 30-50 pertanyaan sawit
4. Bandingkan akurasi: DeepSeek API vs Qwen 27B
5. Keputusan: lanjut DeepSeek API atau migrasi ke lokal

### Catatan
- **Qwen 3.6 27B** — butuh RAM 24-32GB (VPS ~$50-60/bln)
- **Qwen 2.5 7B** — bisa jalan di ROG (RAM 8GB, gratis)
- Kalau Qwen 7B cukup akurat → bisa gratis total tanpa API

---

## Fase 3 — Dataset Fine-tune (2-3 minggu)

### Goal
5.751 file markdown → 10.000-20.000 pasangan QA domain sawit.

### Pipeline

```
5.751 file .md
    ↓
Script Python: baca file → chunk → kirim ke DeepSeek API
    ↓ suruh generate 3-5 QA pair per file
Raw QA pairs (~20.000)
    ↓
Filter: hapus duplikat (>90% similar), perbaiki format
    ↓
Export dua format:
  - JSONL (HuggingFace): {"instruction": "...", "output": "..."}
  - JSONL (OpenAI): {"messages": [
      {"role": "system", "content": "..."},
      {"role": "user", "content": "..."},
      {"role": "assistant", "content": "..."}
    ]}
```

### Hasil
`sawit-qa-dataset.jsonl` — aset permanen untuk fine-tune model apa pun.

---

## Fase 4 — Fine-tune Model Sawit (1-2 minggu setelah dataset jadi)

### Opsi A: Gratis — Qwen 3.6 27B + Unsloth (Kaggle GPU)

| Step | Detail |
|------|--------|
| Platform | Kaggle (30 jam GPU/minggu gratis) atau Google Colab |
| Base model | Qwen 3.6 27B (Apache 2.0, open weights) |
| Metode | QLoRA (8-bit, hemat VRAM) |
| Waktu training | ~4-8 jam |
| Output | `qwen-sawit-27b.gguf` (~16-18 GB quantized Q4) |
| Deploy | Ollama di VPS 32GB RAM |
| **Total biaya** | **$0** |

### Opsi B: Berbayar — DeepSeek Official Fine-tune

| Step | Detail |
|------|--------|
| Upload dataset | `api.deepseek.com/beta/fine_tuning` |
| Base model | `deepseek-chat` |
| Biaya | $5-20 (tergantung jumlah token training) |
| Deploy | Langsung via API, model name kustom |
| **Total biaya** | **$5-20** |

### Catatan
- Opsi A lebih murah dan model jalan offline (bisa dijual on-premise)
- Opsi B lebih mudah (tidak perlu urus infrastruktur)
- **Rekomendasi: mulai dengan Opsi A (gratis)**

---

## Fase 5 — Produk Komersial (setelah fine-tune)

### Target Pasar

| Segmen | Contoh | Harga |
|--------|--------|-------|
| Perusahaan perkebunan | PTPN, Astra Agro, Sinar Mas | Rp 20-50jt (on-premise) |
| Koperasi sawit | KUD, koperasi petani | Rp 500rb-2jt/tahun (SaaS) |
| Mahasiswa/peneliti | IPB, USU, PPKS | Rp 100rb-500rb/tahun |
| Konsultan kebun | Konsultan swasta | Rp 1-5jt/tahun |

### Feature Set Minimum (MVP)

| Feature | Status |
|---------|--------|
| API RAG with DeepSeek API | ⏳ Fase 1 |
| Fine-tuned model sawit | ⏳ Fase 4 |
| API key authentication | ❌ Belum |
| Dashboard web (Streamlit) | ❌ Belum |
| Docker packaging | ❌ Belum |
| Landing page + pricing | ❌ Belum |
| Payment gateway (Xendit/Midtrans) | ❌ Belum |

---

## Timeline

```
Fase 1: RAG + DeepSeek API       ⬛⬛⬜⬜⬜⬜⬜⬜  (1 minggu)
Fase 2: Benchmark model gratis   ⬜⬛⬛⬜⬜⬜⬜⬜  (2-5 hari)
Fase 3: Dataset QA               ⬜⬜⬛⬛⬛⬜⬜⬜  (2-3 minggu)
Fase 4: Fine-tune                ⬜⬜⬜⬜⬛⬛⬜⬜  (1-2 minggu)
Fase 5: Produk komersial         ⬜⬜⬜⬜⬜⬛⬛⬛  (2-4 minggu)
```

## Catatan Penting

### Model vs Dataset

```
Dataset sawit (10k-20k QA)    ← ASET PERMANEN
        ↓ bisa dipakai untuk model APAPUN
Qwen 3.6 27B → fine-tune → model sawit
Gemma 4     → fine-tune → model sawit
DeepSeek    → fine-tune → model sawit
Llama       → fine-tune → model sawit
```

**Dataset adalah moat.** Model bisa berganti (tiap 3-6 bulan ada versi baru), tapi dataset tetap milik kamu.

### Update Base Model

Saat base model naik versi (Qwen 3.6 → 3.7 open weights):
1. Dataset tetap sama
2. Training ulang 2-6 jam
3. Biaya $5-10 (GPU sewa)
4. Hasil biasanya lebih bagus

Bukan masalah besar. Fokus ke dataset.

---

## Status Saat Ini (Juni 2026)

| Komponen | Status |
|----------|--------|
| RAG corpus (5.741 file sawit) | ✅ Bersih (16 non-sawit dipisah ke Non Sawit/) |
| ChromaDB + ONNX embedding | ✅ Berfungsi (203k chunks, rebuild clean) |
| OPIN UI (chatbot) | ✅ Live di :8000 |
| FastAPI server (systemd) | ✅ Auto-start di ROG |
| DeepSeek API integration | ✅ Fase 1 selesai |
| OpenCode-batch | ❌ Diganti |
| Qwen 3.6 27B test | ❌ Fase 2 (next) |
| Dataset 10k-20k QA | ❌ Fase 3 |
| Fine-tune | ❌ Fase 4 |
| Produk komersial | ❌ Fase 5 |
