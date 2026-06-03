#!/bin/bash
set -e

if [ ! -f "faiss_index.pkl" ]; then
echo "faiss_index.pkl non trovato — eseguo crawler + index_embeddings..."
python crawler.py || true
python index_embeddings.py || true
fi

exec uvicorn backend:app --host 0.0.0.0 --port 8000
