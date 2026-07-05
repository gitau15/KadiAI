# Election Law AI

A RAG-powered Q&A system for Kenyan electoral law. Ask natural language questions and get answers with inline legal citations from the Constitution, Elections Act, IEBC regulations, and landmark election petition judgments.

## Quick Start

```bash
cp .env.example .env
# Edit .env and add your ZHIPU_API_KEY
docker compose up
```

- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs
- Qdrant Dashboard: http://localhost:6333/dashboard

## Ingest Documents

Place PDFs in `backend/data/raw/`, then:

```bash
curl -X POST http://localhost:8000/api/v1/ingest
```

## Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | Vue 3 + TypeScript + Tailwind CSS |
| Backend | FastAPI (async Python) |
| Vector DB | Qdrant (hybrid search) |
| LLM | Zhipu GLM-4-Flash |
| Embeddings | Zhipu embedding-2 (1024d) |
| OCR | Tesseract 5 + OpenCV |

## Disclaimer

This is an AI research tool, not legal advice.
