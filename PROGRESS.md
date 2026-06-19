# Progress — Sawit AI RAG

_Updated: 2026-06-20_

---

## Status Komponen

| Komponen | Status | Catatan |
|----------|--------|---------|
| **Corpus** | ✅ 5.741 file sawit | 16 non-sawit dipisah ke `Non Sawit/` |
| **ChromaDB** | ⏳ Import berjalan | tmux `rag-import`, target full 5741 file |
| **LLM Integration** | ✅ DeepSeek API | `deepseek-chat` via `sdk.openai` |
| **OPIN UI** | ✅ Live | `http://100.116.15.57:8000` |
| **API Server** | ✅ systemd | auto-restart, port 8000 |
| **Sync Mac → ROG** | ✅ launchd | tiap jam via `com.muhdan.sync-rag` |
| **Version Control** | ✅ GitHub | `github.com/muhdansyarovy/rag-deepseek-sawit` |

---

## Fase

| Fase | Status | Target |
|------|--------|--------|
| **Fase 1** — RAG + DeepSeek API | ✅ Selesai | Minggu ini |
| **Fase 2** — Benchmark model gratis | ⏳ | (opsional) |
| **Fase 3** — Dataset fine-tune | ⏳ | 10k-20k QA pairs |
| **Fase 4** — Fine-tune | ⏳ | Qwen 3.6 27B |
| **Fase 5** — Produk komersial | ⏳ | Docker + dashboard |

---

## Detail Progress

### Corpus Files

| Folder | Jumlah | Status |
|--------|--------|--------|
| 00. Disertasi & Riset | 2 | ✅ |
| 01. Presentasi | ~150 | ✅ |
| 02. Agronomi & Kultur Teknis | ~200 | ✅ |
| 03. Fisiologi & Lingkungan | ~50 | ✅ |
| 04. Pemupukan & Nutrisi | ~65 | ✅ |
| 05. Buku & Referensi/Buku | 593 | ✅ (16 non-sawit dipisah) |
| 05. Buku & Referensi/Seri Buku Populer | 1.908 | ✅ |
| 05. Buku & Referensi/My EndNote Library | 6 | ✅ |
| 06. Jurnal & Publikasi/Zotero | ~242 | ✅ |
| 06. Jurnal & Publikasi/PPKS | ~1.384 | ✅ |
| 06. Jurnal & Publikasi/2019 + 2020 | 4 | ✅ |
| 07. Tools & Software | ~10 | ✅ |
| 08. Presentasi Eksternal | ~50 | ✅ |
| 09. Training & Workshop | ~10 | ✅ |
| 10. Gambar & Media | ~10 | ✅ |
| 11. KAK & Dokumen Kebun | 12 | ✅ |
| 12. Draft & Review AI | 5 | ✅ |
| **Total** | **5.741** | **Bersih sawit** |

### Vector DB

| Metric | Nilai |
|--------|-------|
| Total chunks | 203k+ (masuk) |
| Target chunks | ~150k-200k (final) |
| Embedding model | all-MiniLM-L6-v2 (384d) |
| Distance metric | Cosine |
| DB path | `db/` |

### Infrastructure

| Server | Detail |
|--------|--------|
| Hostname | ROG (Linux Mint) |
| IP (Tailscale) | 100.116.15.57 |
| Port | 8000 |
| Service | systemd `rag-sawit.service` |
| Import session | tmux `rag-import` |
| Python | 3.12.3 (venv) |
| RAM | ~300MB peak (server) |

### Biaya Terkini

| Item | Biaya/bln |
|------|-----------|
| DeepSeek API (100 query/hari) | ~$1-2 |
| Listrik ROG | existing |
| Tailscale | gratis |
| **Total** | **~$1-2/bln** |

---

## Untuk AI yang Melanjutkan

Baca `README.md` untuk arsitektur lengkap. Baca `ROADMAP.md` untuk rencana ke depan. Baca `CHANGELOG.md` untuk riwayat perubahan.

### Commands Penting

```bash
# Cek import progress
ssh rog 'tmux capture-pane -t rag-import -p -S -3'

# Cek status server
ssh rog 'sudo systemctl status rag-sawit.service'

# Restart server
ssh rog 'sudo systemctl restart rag-sawit.service'

# Test query
curl http://100.116.15.57:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Apa itu pupuk NPK?"}'
```
