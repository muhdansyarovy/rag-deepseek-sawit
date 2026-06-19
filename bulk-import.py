"""bulk-import.py — Batch import markdown files ke ChromaDB
Cara pakai:
    python bulk-import.py ~/RAG\ Corpus/
"""
import sys, os, glob
sys.path.insert(0, os.path.dirname(__file__))
from rag import add_knowledge, get_collection

def import_dir(root_dir):
    root_dir = os.path.abspath(root_dir)
    if not os.path.exists(root_dir):
        print(f"❌ Folder tidak ditemukan: {root_dir}")
        return
    
    files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for f in filenames:
            if f.endswith(".md"):
                files.append(os.path.join(dirpath, f))
    
    files.sort()
    print(f"📂 Menemukan {len(files)} file .md")
    
    for i, f in enumerate(files):
        rel = os.path.relpath(f, root_dir)
        print(f"  [{i+1}/{len(files)}] {rel}")
        try:
            add_knowledge(f)
        except Exception as e:
            print(f"    ⚠️ Gagal: {e}")
    
    col = get_collection()
    print(f"\n✅ Total chunks di DB: {col.count()}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__.strip())
        sys.exit(1)
    import_dir(sys.argv[1])
