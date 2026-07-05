from pathlib import Path
from fastapi import APIRouter, Depends, BackgroundTasks

from app.api.deps import get_retriever
from app.services.ingestion import IngestionService
from app.services.retrieval import RetrievalService

router = APIRouter(tags=["ingest"])

DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"


@router.post("/ingest")
async def ingest_documents(
    background_tasks: BackgroundTasks,
    retriever: RetrievalService = Depends(get_retriever),
):
    pdfs = list(RAW_DIR.glob("*.pdf"))
    if not pdfs:
        return {"message": "No PDF files found", "files": 0}

    service = IngestionService(retriever)
    background_tasks.add_task(service.run, pdfs)

    return {
        "message": "Ingestion started",
        "files": len(pdfs),
        "filenames": [p.name for p in pdfs],
    }
