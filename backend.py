from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import time
import pickle
from pydantic import BaseModel
from typing import List
from tinydb import TinyDB, Query

app = FastAPI(title="IMSA Chatbot (FAISS prototype)")

#Allow CORS for demo; restrict in production
app.add_middleware(

CORSMiddleware,
allow_origins=["*"],
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)

DB_FILE = "sessions.json"
db = TinyDB(DB_FILE)
SESSIONS_TABLE = db.table("sessions")
QUEUE_TABLE = db.table("queue")

FAISS_FILE = "faiss_index.pkl"
if not os.path.exists(FAISS_FILE):

# warning message must be indented (it's inside the if block)
print("Warning: faiss_index.pkl not found. Run index_embeddings.py first.")
#Load FAISS index and sentence-transformers model
MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)
if OPENAI_API_KEY:

import openai
openai.api_key = OPENAI_API_KEY
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

sbert = SentenceTransformer("all-MiniLM-L6-v2")
faiss_data = None
if os.path.exists(FAISS_FILE):

with open(FAISS_FILE, "rb") as f:
    faiss_data = pickle.load(f)
index = faiss_data["index"]
metadatas = faiss_data["metadatas"]
texts = faiss_data["texts"]
else:

index = None
metadatas = []
texts = []
class ChatReq(BaseModel):

session_id: str
message: str
def retrieve(query, top_k=4):

if index is None:
    return []
qv = sbert.encode([query]).astype("float32")
faiss.normalize_L2(qv)
D, I = index.search(qv, top_k)
results = []
for idx in I[0]:
    if idx < 0 or idx >= len(texts):
        continue
    results.append({"text": texts[idx], "meta": metadatas[idx]})
return results
SYSTEM_PROMPT = """Sei un assistente per IMSA SRL. Rispondi in italiano, tono formale ma cordiale. Usa sempre i contenuti forniti (seguiti da link) per rispondere. Se non trovi risposta, suggerisci di contattare un operatore."""

@app.post("/chat")
async def chat(req: ChatReq):

# store user message
sid = req.session_id
SESSIONS_TABLE.insert({'session_id': sid, 'from': 'user', 'text': req.message, 'ts': time.time()})
candidates = retrieve(req.message, top_k=4)
context = "\n\n---\n\n".join([f"Fonte: {c['meta']['url']}\n{c['text']}" for c in candidates])
if OPENAI_API_KEY:
    prompt = [
        {"role":"system","content":SYSTEM_PROMPT},
        {"role":"user","content": f"Domanda: {req.message}\n\nContenuti rilevanti:\n{context}\n\nRispondi in italiano, cita le fonti linkando le URL se rilevante."}
    ]
    try:
        resp = openai.ChatCompletion.create(model=MODEL, messages=prompt, max_tokens=700, temperature=0.1)
        answer = resp["choices"][0]["message"]["content"]
    except Exception as e:
        answer = ("Errore nel chiamare l'API LLM. Messaggio: " + str(e) +
                  "\n\nEcco i contenuti rilevanti:\n" + context)
else:
    # Fallback semplice: concatenazione sintetica
    if candidates:
        snippets = "\n\n".join([f"- {c['meta']['url']}: {c['text'][:400].strip()}..." for c in candidates])
        answer = ("Non ho una chiave LLM configurata. Ecco i contenuti più rilevanti che ho trovato:\n\n" +
                  snippets + "\n\nSe vuoi una risposta più elaborata, configura OPENAI_API_KEY.")
    else:
        answer = ("Non ho trovato informazioni rilevanti nel sito. Puoi richiedere assistenza da un operatore "
                  "cliccando su 'Parla con un operatore' nel widget.")
# store bot answer
SESSIONS_TABLE.insert({'session_id': sid, 'from': 'bot', 'text': answer, 'ts': time.time()})
return {"answer": answer, "sources": [c["meta"]["url"] for c in candidates]}
@app.post("/handoff")
async def handoff(req: ChatReq):

sid = req.session_id
# append to queue and store the message
QUEUE_TABLE.insert({'session_id': sid, 'message': req.message, 'ts': time.time(), 'status':'open'})
SESSIONS_TABLE.insert({'session_id': sid, 'from': 'user', 'text': f"[HANDOFF] {req.message}", 'ts': time.time()})
return {"ok": True, "message": "Richiesta inoltrata all'operatore. Verrai contattato a breve."}
@app.get("/operator/queue")
async def operator_queue():

items = QUEUE_TABLE.all()
return {"queue": items}
@app.post("/operator/send")
async def operator_send(payload: dict):

sid = payload.get("session_id")
text = payload.get("text")
if not sid or not text:
    raise HTTPException(status_code=400, detail="session_id e text richiesti")
# add operator message to session
SESSIONS_TABLE.insert({'session_id': sid, 'from': 'operator', 'text': text, 'ts': time.time()})
# mark queue item as handled (first matching)
Q = Query()
res = QUEUE_TABLE.search(Q.session_id == sid)
if res:
    for item in res:
        QUEUE_TABLE.update({'status':'handled'}, doc_ids=[item.doc_id])
return {"ok": True}
@app.get("/session/{session_id}")
async def get_session(session_id: str):

msgs = SESSIONS_TABLE.search(Query().session_id == session_id)
# sort by ts
msgs_sorted = sorted(msgs, key=lambda x: x.get('ts', 0))
return {"messages": msgs_sorted}
if name == "main":

import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8000)
