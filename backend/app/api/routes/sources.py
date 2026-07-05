from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_retriever
from app.models.source import SourceDocument, SourceContext
from app.services.retrieval import RetrievalService

router = APIRouter(tags=["sources"])


@router.get("/sources", response_model=list[SourceDocument])
async def list_sources(retriever: RetrievalService = Depends(get_retriever)):
    return await retriever.list_documents()


@router.get("/sources/{chunk_id}/context", response_model=SourceContext)
async def get_context(chunk_id: str, retriever: RetrievalService = Depends(get_retriever)):
    chunk = await retriever.get_chunk(chunk_id)
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found")
    return chunk
