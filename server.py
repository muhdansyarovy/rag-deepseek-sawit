"""server.py — API Server untuk Sawit AI RAG
Jalankan: uvicorn server:app --host 0.0.0.0 --port 8000

Endpoint:
    POST /ask        -> tanya
    POST /knowledge  -> upload dokumen
    GET  /health     -> status
    GET  /stats      -> statistik DB
    GET  /models     -> daftar model
"""
import os
import tempfile
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from rag import ask, add_knowledge, get_collection, DEEPSEEK_MODEL

app = FastAPI(title="Sawit AI RAG API", version="2.0.0")

class AskRequest(BaseModel):
    question: str

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
        "model": DEEPSEEK_MODEL
    }

@app.post("/ask", response_model=AskResponse)
def ask_endpoint(req: AskRequest):
    answer, sources = ask(req.question)
    return AskResponse(answer=answer, model=DEEPSEEK_MODEL, sources=sources)

@app.post("/knowledge")
async def upload_knowledge(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename or "file.txt")[1] or ".txt"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False, mode="wb") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    os.makedirs("knowledge", exist_ok=True)
    perm_path = os.path.join("knowledge", file.filename or "uploaded.txt")
    with open(perm_path, "wb") as f:
        f.write(content)

    try:
        add_knowledge(tmp_path)
        return {"status": "ok", "file": file.filename, "message": "Knowledge added"}
    finally:
        os.unlink(tmp_path)

@app.get("/models")
def list_models():
    return {
        "model": DEEPSEEK_MODEL
    }
