import time
from fastapi import APIRouter, Depends

from app.api.deps import get_retriever, get_generator
from app.models.query import QueryRequest, QueryResponse, Citation
from app.services.retrieval import RetrievalService
from app.services.generation import GenerationService

router = APIRouter(tags=["query"])


@router.post("/query", response_model=QueryResponse)
async def query(
    req: QueryRequest,
    retriever: RetrievalService = Depends(get_retriever),
    generator: GenerationService = Depends(get_generator),
):
    start = time.time()

    chunks = await retriever.hybrid_search(req.query, top_k=req.top_k, embedder=generator.embed)
    answer, raw_citations = await generator.generate(req.query, chunks)

    citations = [
        Citation(
            document=c["document"],
            section=c["section"],
            page=c["page"],
            chunk_text=c["chunk_text"][:300],
            chunk_id=c["chunk_id"],
        )
        for c in raw_citations
    ]

    elapsed = (time.time() - start) * 1000
    return QueryResponse(
        query=req.query,
        answer=answer,
        citations=citations,
        processing_time_ms=round(elapsed, 1),
    )
