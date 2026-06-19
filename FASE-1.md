# Fase 1 — RAG + DeepSeek API

## Tujuan
Ganti `opencode-batch` (CLI subprocess) → DeepSeek API langsung via HTTP. API RAG berjalan 24/7 dengan biaya minimal.

---

## Perubahan File

### 1. `rag.py`

| Yang Berubah | Detail |
|---|---|
| Hapus | `import subprocess` |
| Hapus | `AVAILABLE_MODELS` (deepseek-v4-flash-free, big-pickle, dll) |
| Hapus | `OPCODE_BATCH` constant |
| Hapus | `--model`, `--list-models` dari CLI arguments |
| Ganti nama | `DEFAULT_MODEL` → `DEEPSEEK_MODEL` |
| Tambah | `from openai import OpenAI` |
| Tambah | `from dotenv import load_dotenv` + `load_dotenv()` |
| Tambah | `DEEPSEEK_API_KEY` dari `.env` |
| Fungsi `ask()` | Hapus subprocess `opencode-batch` → ganti dengan `client.chat.completions.create()` |

#### Fungsi `ask()` — Sebelum vs Sesudah

**Sebelum:**
```python
result = subprocess.run(
    [OPCODE_BATCH, prompt, full_model],
    capture_output=True, text=True, timeout=120
)
output = result.stdout
answer = output.split("JAWABAN:")[-1].strip()
```

**Sesudah:**
```python
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt}
]

response = client.chat.completions.create(
    model=DEEPSEEK_MODEL,
    messages=messages,
    temperature=0.3,
    max_tokens=2000
)

answer = response.choices[0].message.content
```

### 2. `server.py`

| Yang Berubah | Detail |
|---|---|
| Import | Hapus `AVAILABLE_MODELS`, `DEFAULT_MODEL` dari import rag |
| Tambah import | `DEEPSEEK_MODEL` dari rag |
| `AskRequest.model` | Default jadi `DEEPSEEK_MODEL` |
| Fungsi `ask_endpoint()` | Hapus `redirect_stdout` + parsing output. `ask()` langsung return `(answer, sources)` |
| Endpoint `/models` | Kembalikan daftar model DeepSeek yang tersedia |

### 3. `.env` (file baru)

```
DEEPSEEK_API_KEY=sk-isinya-api-key-kamu
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
```

### 4. `requirements.txt`

Tambah:
```
openai
python-dotenv
```

### 5. `.gitignore`

Tambah:
```
.env
```

---

## Alur Setelah Fase 1

```
🧑 User: "Apa dosis pupuk NPK untuk TBM?"
       │
       ▼
   POST /ask → server.py → rag.ask()
       │
       ├─ 1. ChromaDB query (cari 3 chunk relevan)
       │
       ├─ 2. Susun prompt (konteks + pertanyaan)
       │
       ├─ 3. POST ke api.deepseek.com/v1/chat/completions
       │      └─ model: deepseek-chat
       │      └─ messages: [{system}, {user}]
       │
       ├─ 4. Parse response
       │
       ▼
   💬 Jawaban + sumber file
```

---

## Model Tersedia

| Nama | Model ID | Kegunaan |
|------|----------|----------|
| `deepseek-chat` | `deepseek-chat` | Default, cepat, akurat untuk tanya jawab (V3) |
| `deepseek-reasoner` | `deepseek-reasoner` | Untuk penalaran kompleks (R1), lebih lambat |

Default: `deepseek-chat`

---

## Biaya

| Pemakaian | Token/bln | Biaya |
|---|---|---|
| Personal (~100 query/hari) | ~3-5M token | ~$1-2/bln |
| Produk (~1.000 query/hari) | ~30-50M token | ~$5-10/bln |

---

## File Sebelum dan Sesudah

### Sebelum (sekarang)
```
rag.py          → 292 baris, subprocess ke opencode-batch
server.py       → 120 baris, parsing stdout
.env            → tidak ada
requirements    → chromadb, fastapi, uvicorn, python-multipart
```

### Sesudah
```
rag.py          → ~250 baris, HTTP call ke DeepSeek API
server.py       → ~100 baris, langsung return object
.env            → API key + config
requirements    → tambah openai, python-dotenv
```

---

## Cara Test

1. Export / set `.env`:
```
DEEPSEEK_API_KEY=sk-xxx
DEEPSEEK_MODEL=deepseek-chat
```

2. Test via CLI:
```bash
python rag.py --ask "Apa itu pupuk NPK untuk sawit?"
```

3. Test via API:
```bash
curl http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Apa itu pupuk NPK untuk sawit?"}'
```
