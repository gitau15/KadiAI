import asyncio
import json
import re
import httpx

from app.core.config import settings

SYSTEM_PROMPT = """You are a Kenyan election law assistant. Answer the question using ONLY the provided context below.

Rules:
1. Cite the document name, section/article, and page for EVERY claim you make.
2. Format citations inline as: [Source: Document Name, Section X, Page Y]
3. If the context does not contain sufficient information to answer, say: "I cannot find a definitive answer in the documents I have access to."
4. Do not guess or use external knowledge.
5. Be concise and direct. Use plain English.

Context:
{context}"""

API_BASE = "https://open.bigmodel.cn/api/paas/v4"


class GenerationService:
    def __init__(self):
        self.api_key = settings.zhipu_api_key
        self.llm_model = settings.llm_model
        self.embedding_model = settings.embedding_model
        if settings.use_local_embedding:
            from sentence_transformers import SentenceTransformer
            self._local_embed_model = SentenceTransformer(settings.local_embedding_model)
        else:
            self._local_embed_model = None

    async def embed(self, text: str) -> list[float]:
        if self._local_embed_model is not None:
            embedding = self._local_embed_model.encode(text, normalize_embeddings=True)
            return embedding.tolist()
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{API_BASE}/embeddings",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"model": self.embedding_model, "input": text},
            )
            resp.raise_for_status()
            return resp.json()["data"][0]["embedding"]

    async def generate(self, query: str, chunks: list[dict]) -> tuple[str, list[dict]]:
        context_parts = []
        citations_map = []

        for i, chunk in enumerate(chunks):
            source_tag = (
                f"[Source: {chunk['document']}, "
                f"{chunk.get('section', 'N/A')}, "
                f"Page {chunk.get('page', 'N/A')}]"
            )
            context_parts.append(f"{source_tag}\n{chunk['chunk_text']}")
            citations_map.append(
                {
                    "document": chunk["document"],
                    "section": chunk.get("section", ""),
                    "page": chunk.get("page", 0),
                    "chunk_text": chunk["chunk_text"],
                    "chunk_id": chunk.get("chunk_id", ""),
                }
            )

        context = "\n\n---\n\n".join(context_parts)
        prompt = SYSTEM_PROMPT.format(context=context)

        async with httpx.AsyncClient(timeout=300) as client:
            resp = await client.post(
                f"{API_BASE}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.llm_model,
                    "messages": [
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": query},
                    ],
                    "temperature": 0.1,
                    "max_tokens": 2048,
                },
            )
            resp.raise_for_status()
            data = resp.json()

        answer = data["choices"][0]["message"]["content"]

        # Match cited chunks to return structured citations
        used_citations = self._extract_used_citations(answer, citations_map)

        return answer, used_citations

    def _extract_used_citations(
        self, answer: str, citations_map: list[dict]
    ) -> list[dict]:
        """Return only citations whose documents are mentioned in the answer."""
        used = []
        seen = set()
        for cit in citations_map:
            doc_name = cit["document"].lower()
            if doc_name in answer.lower() and doc_name not in seen:
                seen.add(doc_name)
                used.append(cit)
        return used or citations_map[:3]
