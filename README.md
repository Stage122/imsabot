# Chatbot IMSA SRL — Prototipo (FAISS locale)

Questo progetto è un prototipo RAG che indicizza il sito https://www.imsasrl.it usando FAISS locale e sentence-transformers, espone un'API FastAPI per la chat e include:
- crawler.py — estrae contenuti dal sito e salva `pages.json`
- index_embeddings.py — crea embeddings e popola FAISS (`faiss_index.pkl`)
- backend.py — FastAPI con endpoint `/chat`, `/handoff`, `/operator/queue`, `/operator/send`, `/session/{id}`
- widget.js — snippet da inserire nelle pagine del sito
- dashboard.html — interfaccia web per operatori
- Dockerfile + docker-compose.yml — per avviare tutto in container (opzionale)
- requirements.txt — dipendenze Python

- Nota: per risposte generative puoi impostare OPENAI_API_KEY; senza la chiave il backend usa un fallback con estratti.
