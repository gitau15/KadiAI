from pathlib import Path
from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel

from app.api.deps import get_retriever
from app.services.retrieval import RetrievalService
from app.services.ingestion import IngestionService
from app.scraper.kenya_law import KenyaLawScraper
from app.scheduler import get_status, run_scrape_and_ingest

router = APIRouter(tags=["scrape"])

RAW_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "raw"


class ScrapeRequest(BaseModel):
    max_pages: int = 3
    auto_ingest: bool = True


@router.post("/scrape")
async def scrape_kenyalaw(
    req: ScrapeRequest,
    background_tasks: BackgroundTasks,
    retriever: RetrievalService = Depends(get_retriever),
):
    scraper = KenyaLawScraper(output_dir=RAW_DIR, max_pages=req.max_pages)

    async def _run():
        # Run scraper in thread (it's synchronous due to httpx sync client)
        import asyncio
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, scraper.run)

        # Auto-ingest newly downloaded PDFs
        if req.auto_ingest and result.documents_downloaded > 0:
            pdfs = list(RAW_DIR.glob("*.pdf"))
            ingestion = IngestionService(retriever)
            await ingestion.run(pdfs)

        return {
            "documents_found": result.documents_found,
            "documents_downloaded": result.documents_downloaded,
            "documents_skipped": result.documents_skipped,
            "errors": result.errors[:10],
            "downloaded_files": [Path(f).name for f in result.downloaded_files],
        }

    background_tasks.add_task(_run)
    return {"message": "Scraping started in background", "max_pages": req.max_pages}


@router.get("/scheduler/status")
async def scheduler_status():
    """Check the weekly scheduler status and next run time."""
    return get_status()


@router.post("/scheduler/run")
async def trigger_manual_run(
    background_tasks: BackgroundTasks,
    retriever: RetrievalService = Depends(get_retriever),
):
    """Manually trigger a scrape + ingest pipeline (same as the scheduled Friday job)."""

    async def _run():
        await run_scrape_and_ingest(max_pages=5, retriever=retriever)

    background_tasks.add_task(_run)
    return {"message": "Manual scrape & ingest started in background"}
