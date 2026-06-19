"""
rag.py — RAG Engine with DeepSeek API

Cara pakai:
    python rag.py --add dokumen.txt
    python rag.py --ask "pertanyaan"
"""

import argparse
import os
import sys
import json
import glob
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

if sys.version_info < (3, 11):
    print("Python 3.11+ required")
    sys.exit(1)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")

if not DEEPSEEK_API_KEY:
    print("DEEPSEEK_API_KEY not set in .env")
    sys.exit(1)

DB_DIR = os.path.join(os.path.dirname(__file__), "db")
KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "knowledge")
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

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

def chunk_text(text, filename):
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

def add_knowledge(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    print(f"Reading: {filepath}")
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    filename = os.path.basename(filepath)
    chunks = chunk_text(text, filename)
    print(f"   -> {len(chunks)} chunks")

    if not chunks:
        print("No text to process")
        return

    texts = [c["text"] for c in chunks]
    metas = [{"source": c["source"], "chunk_id": str(c["chunk_id"])} for c in chunks]
    ids = [f"{filename}_{c['chunk_id']}" for c in chunks]

    collection = get_collection()

    existing = collection.get(ids=ids)
    if existing and existing["ids"]:
        print(f"   {len(existing['ids'])} chunks skipped (duplicates)")
        new_ids = [i for i in ids if i not in existing["ids"]]
        if not new_ids:
            print("All already in DB")
            return
        ids = new_ids
        idx_map = {i: idx for idx, i in enumerate(ids)}
        texts = [texts[idx_map[i]] for i in ids]
        metas = [metas[idx_map[i]] for i in ids]

    print("Embedding & saving...")
    collection.add(ids=ids, documents=texts, metadatas=metas)
    print(f"{len(ids)} chunks added (total: {collection.count()})")

def ask(question, top_k=3):
    collection = get_collection()
    total = collection.count()

    if total == 0:
        msg = "Database is empty. Add documents first."
        print(msg)
        return msg, []

    print("Searching relevant documents...")
    results = collection.query(query_texts=[question], n_results=min(top_k, total))

    contexts = []
    sources = set()
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        contexts.append(doc)
        sources.add(meta.get("source", "?"))

    context_text = "\n\n---\n\n".join(contexts)
    source_list = sorted(sources)

    system_prompt = "Anda adalah asisten AI ahli budidaya kelapa sawit. Jawab berdasarkan konteks yang diberikan. Jika konteks tidak cukup, katakan 'Tidak ditemukan dalam dokumen.' Jawab dalam Bahasa Indonesia. Sebutkan sumbernya."

    user_prompt = f"KONTEKS:\n{context_text}\n\nPERTANYAAN:\n{question}"

    print(f"Calling DeepSeek API ({DEEPSEEK_MODEL})...")

    try:
        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        answer = f"Error calling DeepSeek API: {e}"
        print(answer)
        return answer, list(source_list)

    print(f"\nAnswer ({DEEPSEEK_MODEL}):")
    print(answer)
    print(f"\nSources: {', '.join(source_list)}")

    return answer, list(source_list)

def add_all_knowledge():
    if not os.path.exists(KNOWLEDGE_DIR):
        os.makedirs(KNOWLEDGE_DIR)
        print(f"Created {KNOWLEDGE_DIR}")
        return

    files = glob.glob(os.path.join(KNOWLEDGE_DIR, "*.txt")) + \
            glob.glob(os.path.join(KNOWLEDGE_DIR, "*.md")) + \
            glob.glob(os.path.join(KNOWLEDGE_DIR, "*.csv"))

    if not files:
        print(f"No .txt/.md/.csv files in {KNOWLEDGE_DIR}")
        return

    for f in files:
        add_knowledge(f)

    col = get_collection()
    print(f"\nTotal chunks in DB: {col.count()}")

def main():
    parser = argparse.ArgumentParser(description="Sawit AI — RAG Engine")
    parser.add_argument("--add", help="Add file to knowledge base")
    parser.add_argument("--add-all", action="store_true", help="Add all files from knowledge/")
    parser.add_argument("--ask", help="Ask a question")
    parser.add_argument("--stats", action="store_true", help="Database statistics")

    args = parser.parse_args()

    if args.stats:
        try:
            col = get_collection()
            count = col.count()
            print(f"Total chunks: {count}")
            if count > 0:
                samples = col.get(limit=5)
                for i, (meta, doc) in enumerate(zip(samples["metadatas"], samples["documents"])):
                    print(f"  [{i+1}] {meta.get('source','?')} - {doc[:80]}...")
        except Exception as e:
            print(f"Database error: {e}")
        return

    if args.add:
        add_knowledge(args.add)
        return

    if args.add_all:
        add_all_knowledge()
        return

    if args.ask:
        ask(args.ask)
        return

    parser.print_help()

if __name__ == "__main__":
    main()
