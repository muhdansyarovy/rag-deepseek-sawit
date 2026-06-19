"""server.py — API Server untuk RAG DeepSeek Sawit
Jalankan: uvicorn server:app --host 0.0.0.0 --port 8000

Endpoint:
    POST /ask        → tanya
    POST /knowledge  → upload dokumen
    GET  /health     → status
    GET  /stats      → statistik DB
"""
import os
import tempfile
from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from rag import ask, add_knowledge, get_collection, AVAILABLE_MODELS, DEFAULT_MODEL

app = FastAPI(title="DeepSeek Sawit RAG API", version="1.0.0")

class AskRequest(BaseModel):
    question: str
    model: str = DEFAULT_MODEL

class AskResponse(BaseModel):
    answer: str
    model: str
    sources: list[str] = []

@app.get("/health")
def health():
    try:
        col = get_collection()
        return {"status": "ok", "chunks": col.count()}
    except:
        return {"status": "ok", "chunks": 0}

@app.get("/stats")
def stats():
    col = get_collection()
    count = col.count()
    return {
        "chunks": count,
        "db_path": os.path.abspath("db"),
        "models": list(AVAILABLE_MODELS.keys()),
        "default_model": DEFAULT_MODEL
    }

@app.post("/ask", response_model=AskResponse)
def ask_endpoint(req: AskRequest):
    if req.model not in AVAILABLE_MODELS:
        return AskResponse(
            answer=f"Model '{req.model}' tidak dikenal. Pilihan: {', '.join(AVAILABLE_MODELS.keys())}",
            model=req.model,
            sources=[]
        )
    
    # Capture output dari fungsi ask
    import io
    import sys
    from contextlib import redirect_stdout
    
    f = io.StringIO()
    with redirect_stdout(f):
        ask(req.question, req.model)
    
    # Parse output
    output = f.getvalue()
    lines = output.split("\n")
    
    # Ambil jawaban (baris setelah "Jawaban (...):")
    answer = ""
    sources = []
    for line in lines:
        if line.startswith("📚 Sumber:"):
            sources = [s.strip() for s in line.replace("📚 Sumber:", "").split(",")]
    
    # Cari bagian jawaban
    in_answer = False
    for line in lines:
        if line.startswith("📝 Jawaban"):
            in_answer = True
            continue
        if in_answer and line.strip():
            answer += line.strip() + "\n"
    
    answer = answer.strip()
    if not answer:
        # Fallback: ambil output terakhir
        for line in reversed(lines):
            if line.strip() and not line.startswith("⏳") and not line.startswith("🔍") and not line.startswith("🤖") and not line.startswith("📚"):
                answer = line.strip()
                break
    
    return AskResponse(answer=answer, model=req.model, sources=sources)

@app.post("/knowledge")
async def upload_knowledge(file: UploadFile = File(...)):
    # Simpan file sementara
    suffix = os.path.splitext(file.filename or "file.txt")[1] or ".txt"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False, mode="wb") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    # Simpan ke folder knowledge/ permanen
    os.makedirs("knowledge", exist_ok=True)
    perm_path = os.path.join("knowledge", file.filename or "uploaded.txt")
    with open(perm_path, "wb") as f:
        f.write(content)
    
    try:
        add_knowledge(tmp_path)
        return {"status": "ok", "file": file.filename, "message": "Pengetahuan ditambahkan"}
    finally:
        os.unlink(tmp_path)

@app.get("/models")
def list_models():
    return {
        "models": AVAILABLE_MODELS,
        "default": DEFAULT_MODEL
    }
