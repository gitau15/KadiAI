import time
from pydantic import BaseModel, Field
from typing import Optional


class Citation(BaseModel):
    document: str
    section: str
    page: int
    chunk_text: str
    chunk_id: str


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)
    session_id: Optional[str] = None


class QueryResponse(BaseModel):
    query: str
    answer: str
    citations: list[Citation]
    processing_time_ms: float
    session_id: Optional[str] = None
