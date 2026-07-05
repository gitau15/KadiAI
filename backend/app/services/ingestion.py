import json
import hashlib
from pathlib import Path
from datetime import datetime

from app.services.retrieval import RetrievalService
from app.ingestion.classifier import classify_pdf
from app.ingestion.extractors import extract_text
from app.ingestion.cleaner import clean_text
from app.ingestion.sectioner import detect_sections
from app.ingestion.chunker import chunk_text
from app.ingestion.embedder import Embedder

MANIFEST_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "ingested.json"


class IngestionService:
    def __init__(self, retriever: RetrievalService):
        self.retriever = retriever
        self.embedder = Embedder()

    async def run(self, pdf_paths: list[Path]):
        manifest = self._load_manifest()

        for pdf_path in pdf_paths:
            doc_id = self._doc_id(pdf_path)
            if doc_id in manifest:
                continue

            pdf_type = classify_pdf(pdf_path)
            raw_text = extract_text(pdf_path, pdf_type)
            cleaned = clean_text(raw_text)
            sections = detect_sections(cleaned)
            chunks = chunk_text(cleaned, sections, pdf_path.name)

            await self.retriever.upsert_chunks(chunks, self.embedder.embed)

            manifest[doc_id] = {
                "filename": pdf_path.name,
                "type": pdf_type,
                "chunks": len(chunks),
                "ingested_at": datetime.utcnow().isoformat(),
            }
            self._save_manifest(manifest)

    def _doc_id(self, path: Path) -> str:
        return hashlib.md5(path.name.encode()).hexdigest()[:12]

    def _load_manifest(self) -> dict:
        if MANIFEST_PATH.exists():
            return json.loads(MANIFEST_PATH.read_text())
        return {}

    def _save_manifest(self, manifest: dict):
        MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, default=str))
