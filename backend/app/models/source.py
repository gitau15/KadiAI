from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SourceDocument(BaseModel):
    id: str
    title: str
    document_type: str  # "statute" or "case_law"
    page_count: int
    ingested_at: Optional[datetime] = None
    source_url: Optional[str] = None


class SourceContext(BaseModel):
    chunk_id: str
    document: str
    section: str
    page: int
    chunk_text: str
    previous_chunk_text: Optional[str] = None
    next_chunk_text: Optional[str] = None
