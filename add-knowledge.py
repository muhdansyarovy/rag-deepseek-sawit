"""add-knowledge.py — CLI untuk tambah pengetahuan ke RAG

Cara pakai:
    python add-knowledge.py dokumen.txt
    python add-knowledge.py knowledge/*.txt
    python add-knowledge.py --watch   # pantau folder knowledge/
"""
import sys
import os
from rag import add_knowledge, add_all_knowledge

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Gunakan:")
        print(f"  python {sys.argv[0]} file.txt")
        print(f"  python {sys.argv[0]} '*.txt'")
        print(f"  python {sys.argv[0]} --all    # semua file di knowledge/")
        sys.exit(1)
    
    if sys.argv[1] == "--all" or sys.argv[1] == "-a":
        add_all_knowledge()
    elif sys.argv[1] == "--watch" or sys.argv[1] == "-w":
        print("📁 Mode watch belum diimplementasi")
        print("   Gunakan: python add-knowledge.py --all")
    else:
        for pattern in sys.argv[1:]:
            import glob
            for f in glob.glob(pattern):
                add_knowledge(f)
