index_embeddings.py
import os
import json
from tqdm import tqdm

PAGES_FILE = "pages.json"
CHUNK_SIZE = 800 # char per chunk
OUT_INDEX = "faiss_index.pkl"

def chunk_text(text, size=CHUNK_SIZE):

parts = []
i = 0
while i < len(text):
    parts.append(text[i:i+size])
    i += size
return parts
def main():

if not os.path.exists(PAGES_FILE):
    raise SystemExit(f"{PAGES_FILE} not found. Run crawler.py first.")
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle

model = SentenceTransformer("all-MiniLM-L6-v2")
with open(PAGES_FILE, encoding="utf-8") as f:
    pages = json.load(f)

buffer = []
for p in tqdm(pages, desc="chunking pages"):
    chunks = chunk_text(p.get("text",""))
    for i, c in enumerate(chunks):
        meta = {"url": p.get("url"), "title": p.get("title"), "chunk_index": i}
        buffer.append((c, meta))

texts = [t for t,m in buffer]
metadatas = [m for t,m in buffer]

print("Computing embeddings (this may take some time)...")
embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

# normalize for cosine similarity with IndexFlatIP
faiss.normalize_L2(embeddings)

dims = embeddings.shape[1]
index = faiss.IndexFlatIP(dims)
index.add(embeddings)

with open(OUT_INDEX, "wb") as f:
    pickle.dump({"index": index, "metadatas": metadatas, "texts": texts}, f)

print(f"Saved FAISS index and metadata to {OUT_INDEX}")
if name == "main":

main()
