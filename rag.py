"""
rag.py — RAG Engine dengan model fleksibel

Cara pakai:
    python rag.py --add dokumen.txt          # masukin dokumen
    python rag.py --ask "pertanyaan"          # pake model default
    python rag.py --ask "pertanyaan" --model big-pickle  # ganti model
    python rag.py --ask "pertanyaan" --model nemotron-3-ultra-free

Model tersedia:
    - deepseek-v4-flash-free  (default, ★ rekomendasi)
    - big-pickle              (paling pintar)
    - mimo-v2.5-free          (cepat)
    - nemotron-3-ultra-free   (reasoning lambat)
    - north-mini-code-free    (ringan)
"""

import argparse
import os
import sys
import subprocess
import json
import glob

# Python minimal 3.11
if sys.version_info < (3, 11):
    print("❌ Minimal Python 3.11. Jalankan: python3.11 rag.py ...")
    sys.exit(1)

# === Konfigurasi ===
DB_DIR = os.path.join(os.path.dirname(__file__), "db")
KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "knowledge")
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# Model yang tersedia
AVAILABLE_MODELS = {
    "deepseek-v4-flash-free": "opencode/deepseek-v4-flash-free",
    "big-pickle": "opencode/big-pickle",
    "mimo-v2.5-free": "opencode/mimo-v2.5-free",
    "nemotron-3-ultra-free": "opencode/nemotron-3-ultra-free",
    "north-mini-code-free": "opencode/north-mini-code-free",
}

DEFAULT_MODEL = "deepseek-v4-flash-free"
OPCODE_BATCH = os.path.expanduser("~/.local/bin/opencode-batch")

# === Embedding + Vector DB (lazy import) ===
_chroma_client = None
_chroma_collection = None

_ef = None
def get_ef():
    global _ef
    if _ef is None:
        from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
        _ef = DefaultEmbeddingFunction()
    return _ef

def get_collection():
    global _chroma_client, _chroma_collection
    if _chroma_collection is None:
        import chromadb
        _chroma_client = chromadb.PersistentClient(path=DB_DIR)
        _chroma_collection = _chroma_client.get_or_create_collection(
            name="deepseek-sawit",
            metadata={"hnsw:space": "cosine"},
            embedding_function=get_ef()
        )
    return _chroma_collection

# === Chunking ===
def chunk_text(text, filename):
    """Potong teks jadi chunks"""
    paragraphs = text.split("\n\n")
    chunks = []
    current = []
    current_len = 0
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if current_len + len(para) > CHUNK_SIZE and current:
            chunks.append("\n\n".join(current))
            current = current[-1:] if CHUNK_OVERLAP else []
            current_len = sum(len(p) for p in current)
        current.append(para)
        current_len += len(para)
    
    if current:
        chunks.append("\n\n".join(current))
    
    return [
        {"text": c, "source": filename, "chunk_id": i}
        for i, c in enumerate(chunks)
    ]

# === Add Knowledge ===
def add_knowledge(filepath):
    """Masukin dokumen ke vector store"""
    if not os.path.exists(filepath):
        print(f"❌ File tidak ditemukan: {filepath}")
        return
    
    print(f"📖 Membaca: {filepath}")
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    
    filename = os.path.basename(filepath)
    chunks = chunk_text(text, filename)
    print(f"   → {len(chunks)} chunks")
    
    if not chunks:
        print("⚠️  Tidak ada teks yang bisa diproses")
        return
    
    texts = [c["text"] for c in chunks]
    metas = [{"source": c["source"], "chunk_id": str(c["chunk_id"])} for c in chunks]
    ids = [f"{filename}_{c['chunk_id']}" for c in chunks]
    
    collection = get_collection()
    
    # Cek duplikat
    existing = collection.get(ids=ids)
    if existing and existing["ids"]:
        print(f"   ⚠️  {len(existing['ids'])} chunks sudah ada, dilewati")
        new_ids = [i for i in ids if i not in existing["ids"]]
        if not new_ids:
            print("✅ Semua sudah terdaftar")
            return
        ids = new_ids
        idx_map = {i: idx for idx, i in enumerate(ids)}
        texts = [texts[idx_map[i]] for i in ids]
        metas = [metas[idx_map[i]] for i in ids]
    
    print("⏳ Embedding & menyimpan...")
    collection.add(ids=ids, documents=texts, metadatas=metas)
    print(f"✅ {len(ids)} chunks ditambahkan ke database")
    print(f"   Total chunks di DB: {collection.count()}")

# === Ask ===
def ask(question, model_name=None, top_k=3):
    """Tanya ke RAG dengan model tertentu"""
    if model_name is None:
        model_name = DEFAULT_MODEL
    
    if model_name not in AVAILABLE_MODELS:
        print(f"❌ Model '{model_name}' tidak dikenal.")
        print(f"   Pilihan: {', '.join(AVAILABLE_MODELS.keys())}")
        return
    
    full_model = AVAILABLE_MODELS[model_name]
    
    # Cari dokumen relevan
    collection = get_collection()
    
    total = collection.count()
    if total == 0:
        print("⚠️  Database kosong. Masukin dokumen dulu:")
        print("   python rag.py --add knowledge/dokumen.txt")
        return
    
    print(f"🔍 Mencari relevansi...")
    results = collection.query(query_texts=[question], n_results=min(top_k, total))
    
    contexts = []
    sources = set()
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        contexts.append(doc)
        sources.add(meta.get("source", "?"))
    
    context_text = "\n\n---\n\n".join(contexts)
    source_list = ", ".join(sorted(sources))
    
    # Prompt ke LLM
    prompt = f"""Anda adalah asisten AI yang menjawab pertanyaan berdasarkan konteks yang diberikan.

KONTEKS:
{context_text}

PERTANYAAN:
{question}

INSTRUKSI:
- Jawab hanya berdasarkan konteks di atas.
- Jika konteks tidak cukup, katakan "Tidak ditemukan dalam dokumen."
- Jawab dalam Bahasa Indonesia.
- Sebutkan sumbernya.

JAWABAN:"""
    
    print(f"🤖 Model: {model_name}")
    print(f"📚 Sumber: {source_list}")
    print(f"⏳ Menjawab...")
    
    if not os.path.exists(OPCODE_BATCH):
        print(f"❌ opencode-batch tidak ditemukan di {OPCODE_BATCH}")
        return
    
    result = subprocess.run(
        [OPCODE_BATCH, prompt, full_model],
        capture_output=True, text=True, timeout=120
    )
    
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr[:200]}")
        return
    
    # Parse output — ambil baris setelah "JAWABAN:"
    output = result.stdout
    if "JAWABAN:" in output:
        answer = output.split("JAWABAN:")[-1].strip()
    else:
        # Coba ambil dari opencode-batch output
        lines = output.strip().split("\n")
        answer = lines[-1].strip() if lines else output.strip()
    
    print(f"\n📝 Jawaban ({model_name}):")
    print(answer)

# === Batch add all ===
def add_all_knowledge():
    """Masukin semua file teks di folder knowledge"""
    if not os.path.exists(KNOWLEDGE_DIR):
        os.makedirs(KNOWLEDGE_DIR)
        print(f"📁 Folder {KNOWLEDGE_DIR} dibuat. Taruh file .txt di sini.")
        return
    
    files = glob.glob(os.path.join(KNOWLEDGE_DIR, "*.txt")) + \
            glob.glob(os.path.join(KNOWLEDGE_DIR, "*.md")) + \
            glob.glob(os.path.join(KNOWLEDGE_DIR, "*.csv"))
    
    if not files:
        print(f"⚠️  Tidak ada file .txt/.md/.csv di {KNOWLEDGE_DIR}")
        return
    
    for f in files:
        add_knowledge(f)
    
    col = get_collection()
    print(f"\n✅ Total chunks di database: {col.count()}")

# === Main ===
def main():
    parser = argparse.ArgumentParser(description="DeepSeek Sawit — RAG Engine")
    parser.add_argument("--add", help="Tambahkan file ke pengetahuan")
    parser.add_argument("--add-all", action="store_true", help="Tambahkan semua file dari knowledge/")
    parser.add_argument("--ask", help="Tanya sesuatu")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Model: {', '.join(AVAILABLE_MODELS.keys())}")
    parser.add_argument("--list-models", action="store_true", help="Tampilkan model yang tersedia")
    parser.add_argument("--stats", action="store_true", help="Statistik database")
    
    args = parser.parse_args()
    
    if args.list_models:
        print("Model tersedia untuk RAG:\n")
        for name, full in AVAILABLE_MODELS.items():
            star = " ★" if name == DEFAULT_MODEL else ""
            print(f"  {name:30s} → {full}{star}")
        print(f"\nDefault: {DEFAULT_MODEL}")
        return
    
    if args.stats:
        try:
            col = get_collection()
            count = col.count()
            print(f"Total chunks di database: {count}")
            if count > 0:
                samples = col.get(limit=5)
                for i, (meta, doc) in enumerate(zip(samples["metadatas"], samples["documents"])):
                    print(f"\n  [{i+1}] {meta.get('source','?')} — {doc[:80]}...")
        except Exception as e:
            print(f"Database belum ada atau kosong: {e}")
        return
    
    if args.add:
        add_knowledge(args.add)
        return
    
    if args.add_all:
        add_all_knowledge()
        return
    
    if args.ask:
        ask(args.ask, args.model)
        return
    
    parser.print_help()

if __name__ == "__main__":
    main()
