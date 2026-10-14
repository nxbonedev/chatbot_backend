# iTel Chatbot API — Render deployment

## Deploy
1. Upload/extract this project into a GitHub repository (Render's standard Python web-service workflow deploys from a connected Git repository).
2. In Render, choose **New → Web Service**, connect the repository, and use the repository root.
3. Render can read `render.yaml`; otherwise use:
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn fast_api.main:app --host 0.0.0.0 --port $PORT`
4. Add `GOOGLE_API_KEY` in Render's Environment settings. Create the key in Google AI Studio. Never commit a real API key.
5. Deploy. Visit `/docs` to test the API.

## API
- `GET /` — service info
- `GET /health` — health check and whether the vector index exists
- `POST /ingest` JSON: `{"url":"https://example.com"}` — crawl a website and create the knowledge base
- `POST /query` JSON: `{"question":"What does this site offer?"}` — query the knowledge base

Example query:
```json
{"question":"What does this site offer?"}
```

## Important deployment notes
- This version uses Google's hosted Gemini embeddings and chat API. It does not require a separate Ollama server.
- You must call `/ingest` after deploying before `/query` can answer from a website.
- On Render instances without a persistent disk, files such as the FAISS index and SQLite chat history can be lost on redeploy/restart. For production, attach a persistent disk mounted at `/var/data`, then set `INDEX_PATH=/var/data/faiss_multipage_index` and `DB_PATH=/var/data/chat_history.db` in Render's environment. A disk may require a paid Render plan.
- Only ingest websites you are authorized to crawl. Keep your Google API key private.
