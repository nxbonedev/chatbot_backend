import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fast_api.schema import url as URLRequest, QueryRequest, QueryResponse
from backend.main import prompt
from backend.ingestion import ingest_site, INDEX_PATH

app = FastAPI(title="iTel Chatbot API", version="1.0.0")

@app.get("/")
def root():
    return {"status": "ok", "service": "iTel Chatbot API", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok", "knowledge_base_ready": INDEX_PATH.is_dir()}

@app.post("/ingest")
def ingest(value: URLRequest):
    try:
        pages, chunks = ingest_site(base_url=value.url)
        return {"status": "success", "message": "Vector index created successfully", "pages": pages, "chunks": chunks}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(exc)}") from exc

@app.post("/query", response_model=QueryResponse)
async def query_endpoint(payload: QueryRequest):
    if not INDEX_PATH.is_dir():
        raise HTTPException(status_code=409, detail="Knowledge base is not initialized. Call POST /ingest first.")
    try:
        result = await prompt(question=payload.question, session_id=payload.session_id, parent_id=payload.parent_id)
        return QueryResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(exc)}") from exc
