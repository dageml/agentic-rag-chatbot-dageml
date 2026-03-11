import os,sys
import time

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from pathlib import Path
import shutil

from ingest import ingest_document
from chat import generate_answer





app = FastAPI()
DATA_DIR = Path("./sample_docs")
DATA_DIR.mkdir(exist_ok=True)

@app.post("/upload")
async def upload_file(file:UploadFile = File(...)):
    ALLOWED = {".txt", ".pdf", ".docx"}
    path = DATA_DIR / file.filename

    if path.suffix not in ALLOWED:
        return {"error": "File type not allowed"}

    with path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    ingest_document(str(path)) #ingest after upload
    
    return {"status": "uploaded successfully", "filename": file.filename}


# - chat
class ChatRequest(BaseModel):
    question: str

@app.post("/chat")
async def chat(request: ChatRequest):
    answer, citations = generate_answer(request.question)
    return {"answer": answer, "citations": citations}

@app.get("/",response_class=HTMLResponse)
async def ui():
    return HTMLResponse(content=Path("index.html").read_text(), status_code=200)
