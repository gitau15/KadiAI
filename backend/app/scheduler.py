"""
Scheduled scraping & ingestion — runs every Friday at 19:00 EAT (16:00 UTC).

Uses APScheduler with AsyncIOScheduler inside the FastAPI process.
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.scraper.kenya_law import KenyaLawScraper
from app.services.ingestion import IngestionService

logger = logging.getLogger(__name__)

RAW_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw"

# EAT = UTC+3, so 19:00 EAT = 16:00 UTC
EAT = timezone(timedelta(hours=3))

# Module-level state
_scheduler: AsyncIOScheduler | None = None
_state = {
    "is_running": False,
    "last_run": None,
    "last_result": None,
    "next_run": None,
}


def get_status() -> dict:
    """Return current scheduler status."""
    status = {
        "enabled": _scheduler is not None and _scheduler.running,
        "is_running": _state["is_running"],
        "last_run": _state["last_run"],
        "last_result": _state["last_result"],
        "next_run": _state["next_run"],
        "schedule": "Every Friday at 19:00 EAT",
    }
    # Update next_run from scheduler
    if _scheduler and _scheduler.running:
        job = _scheduler.get_job("weekly_scrape")
        if job and job.next_run_time:
            status["next_run"] = job.next_run_time.isoformat()
    return status


async def run_scrape_and_ingest(max_pages: int = 5, retriever=None) -> dict:
    """Run scraper + ingestion pipeline. Used by both scheduler and manual trigger."""
    if _state["is_running"]:
        return {"error": "A scrape/ingest job is already running"}

    _state["is_running"] = True
    _state["last_run"] = datetime.now(EAT).isoformat()
    start = asyncio.get_event_loop().time()

    try:
        # 1. Scrape
        logger.info("[Scheduler] Starting weekly scrape...")
        scraper = KenyaLawScraper(output_dir=RAW_DIR, max_pages=max_pages)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, scraper.run)

        scrape_summary = {
            "documents_found": result.documents_found,
            "documents_downloaded": result.documents_downloaded,
            "documents_skipped": result.documents_skipped,
            "errors": result.errors[:10],
            "new_files": [Path(f).name for f in result.downloaded_files],
        }

        # 2. Ingest new documents
        ingest_summary = None
        if retriever and result.documents_downloaded > 0:
            logger.info(f"[Scheduler] Ingesting {result.documents_downloaded} new documents...")
            pdfs = sorted(RAW_DIR.glob("*.pdf"))
            ingestion = IngestionService(retriever)
            await ingestion.run(pdfs)

            # Count manifest
            import json
            manifest_path = Path(__file__).resolve().parent.parent.parent / "data" / "ingested.json"
            if manifest_path.exists():
                manifest = json.loads(manifest_path.read_text())
                ingest_summary = {"total_documents": len(manifest)}

        elapsed = asyncio.get_event_loop().time() - start
        _state["last_result"] = {
            "scrape": scrape_summary,
            "ingest": ingest_summary,
            "elapsed_seconds": round(elapsed, 1),
            "completed_at": datetime.now(EAT).isoformat(),
        }

        logger.info(
            f"[Scheduler] Done in {elapsed:.0f}s: "
            f"{result.documents_downloaded} downloaded, "
            f"{result.documents_skipped} skipped"
        )
        return _state["last_result"]

    except Exception as e:
        logger.error(f"[Scheduler] Pipeline error: {e}", exc_info=True)
        _state["last_result"] = {"error": str(e)}
        return {"error": str(e)}
    finally:
        _state["is_running"] = False


async def _scheduled_job():
    """Called by APScheduler — needs retriever injected at startup."""
    retriever = _job_kwargs.get("retriever")
    await run_scrape_and_ingest(max_pages=5, retriever=retriever)


# Store kwargs injected at startup
_job_kwargs: dict = {}


def start_scheduler(retriever=None) -> AsyncIOScheduler:
    """Initialize and start the APScheduler with the weekly cron job."""
    global _scheduler

    _job_kwargs["retriever"] = retriever

    _scheduler = AsyncIOScheduler(timezone="UTC")

    # Every Friday at 16:00 UTC = 19:00 EAT
    _scheduler.add_job(
        _scheduled_job,
        trigger=CronTrigger(day_of_week="fri", hour=16, minute=0),
        id="weekly_scrape",
        name="Weekly scrape & ingest (Friday 19:00 EAT)",
        replace_existing=True,
        misfire_grace_time=3600,  # Allow 1h grace if server was down
    )

    _scheduler.start()
    logger.info("Scheduler started — next run: Friday 19:00 EAT")
    return _scheduler


def stop_scheduler():
    """Shut down the scheduler gracefully."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
    _scheduler = None
