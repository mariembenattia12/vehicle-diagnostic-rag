import sys
import os
import uuid
import json
from datetime import datetime, timezone
from typing import Optional
from fastapi import UploadFile, File
from faster_whisper import WhisperModel
import tempfile
from dotenv import load_dotenv
load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "rag"))

from pipeline import rag_query

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Assistant de diagnostic vehicule - API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # a restreindre a l'URL du frontend en production
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions = {}  # session_id -> liste d'echanges

LOG_PATH = "data/logs/chat_log.jsonl"
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)


class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    session_id: str
    sources_count: int


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="La question ne peut pas etre vide.")

    session_id = request.session_id or str(uuid.uuid4())

    try:
        answer, sources = rag_query(request.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur du pipeline RAG: {str(e)}")

    sessions.setdefault(session_id, []).append({
        "question": request.question,
        "answer": answer,
    })

    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "question": request.question,
        "answer": answer,
        "sources_count": len(sources),
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    return ChatResponse(answer=answer, session_id=session_id, sources_count=len(sources))


@app.get("/sessions/{session_id}")
def get_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session introuvable.")
    return {"session_id": session_id, "history": sessions[session_id]}

whisper_model = WhisperModel("small", device="cpu", compute_type="int8")


@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
        content = await audio.read()
        tmp.write(content)
        tmp_path = tmp.name

    segments, info = whisper_model.transcribe(tmp_path, language="fr")
    text = " ".join(segment.text for segment in segments).strip()

    os.remove(tmp_path)

    return {"text": text, "language": info.language}

from fastapi.staticfiles import StaticFiles

FRONTEND_BUILD = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
if os.path.isdir(FRONTEND_BUILD):
    app.mount("/", StaticFiles(directory=FRONTEND_BUILD, html=True), name="frontend")