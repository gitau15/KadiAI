from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import query, sources, ingest, scrape
from app.services.retrieval import RetrievalService
from app.services.generation import GenerationService
from app.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    retriever = RetrievalService()
    await retriever.ensure_collection()
    app.state.retriever = retriever
    app.state.generator = GenerationService()

    # Start weekly scrape scheduler (Friday 19:00 EAT)
    start_scheduler(retriever=retriever)

    yield

    stop_scheduler()
    await retriever.close()


app = FastAPI(
    title="KadiAI",
    description="RAG-powered Q&A for Kenyan electoral law",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://kadiai.vercel.app",
        "https://kadi-ai.vercel.app",
        "https://kadiai-git-main-gitau15s-projects.vercel.app",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query.router, prefix="/api/v1")
app.include_router(sources.router, prefix="/api/v1")
app.include_router(ingest.router, prefix="/api/v1")
app.include_router(scrape.router, prefix="/api/v1")


@app.get("/api/v1/health")
async def health():
    from app.scheduler import get_status as scheduler_status
    return {
        "status": "ok",
        "version": "0.2.0",
        "name": "KadiAI",
        "scheduler": scheduler_status()["enabled"],
    }
