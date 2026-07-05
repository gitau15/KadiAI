import uuid
import logging
from typing import Optional

from supabase import create_client, Client

from app.core.config import settings
from app.models.source import SourceDocument, SourceContext

logger = logging.getLogger(__name__)


class RetrievalService:
    def __init__(self):
        self.client: Client = create_client(settings.supabase_url, settings.supabase_key)
        self.dim = settings.embedding_dim

    async def ensure_collection(self):
        """No-op for Supabase — table is created via SQL migration."""
        # Verify connection by doing a simple count
        try:
            result = self.client.table("document_chunks").select("id").limit(1).execute()
            logger.info(f"Supabase connected. Existing chunks: {result.count}")
        except Exception as e:
            logger.warning(f"Supabase table may not exist yet: {e}")
            logger.warning("Run the SQL migration in supabase_migration.sql first.")

    async def hybrid_search(self, query: str, top_k: int = 5, embedder=None) -> list[dict]:
        """Vector similarity search via the match_documents RPC function."""
        if embedder is None:
            from app.services.generation import GenerationService
            gen = GenerationService()
            embedder = gen.embed

        dense_vector = await embedder(query)

        try:
            result = self.client.rpc(
                "match_documents",
                {
                    "query_embedding": dense_vector,
                    "match_count": top_k,
                },
            ).execute()

            return [
                {
                    "score": row.get("similarity", 0),
                    "chunk_id": row["id"],
                    "document": row["document"],
                    "section": row["section"],
                    "page": row["page"],
                    "chunk_index": row["chunk_index"],
                    "chunk_text": row["chunk_text"],
                    "document_id": row["document_id"],
                    "source_url": row["source_url"],
                }
                for row in result.data
            ]
        except Exception as e:
            logger.error(f"Supabase search error: {e}")
            return []

    async def upsert_chunks(self, chunks: list[dict], embedder):
        """Insert chunks with embeddings into Supabase."""
        rows = []
        for ch in chunks:
            text = ch["chunk_text"]
            dense_vec = await embedder(text)

            rows.append({
                "id": ch.get("chunk_id", str(uuid.uuid4())),
                "document": ch.get("document", ""),
                "section": ch.get("section", ""),
                "page": ch.get("page", 0),
                "chunk_index": ch.get("chunk_index", 0),
                "chunk_text": text,
                "document_id": ch.get("document_id", ""),
                "source_url": ch.get("source_url", ""),
                "embedding": dense_vec,
            })

        # Upsert in batches of 100 to avoid payload size limits
        batch_size = 100
        for i in range(0, len(rows), batch_size):
            batch = rows[i : i + batch_size]
            try:
                self.client.table("document_chunks").upsert(
                    batch, on_conflict="id"
                ).execute()
                logger.info(f"  Upserted batch {i // batch_size + 1}: {len(batch)} chunks")
            except Exception as e:
                logger.error(f"  Upsert error on batch {i // batch_size + 1}: {e}")

    async def list_documents(self) -> list[SourceDocument]:
        """List unique documents from Supabase."""
        try:
            # Paginate to get all rows (Supabase default limit is 1000)
            all_rows = []
            offset = 0
            batch = 1000
            while True:
                result = (
                    self.client.table("document_chunks")
                    .select("document_id, document, source_url, created_at")
                    .range(offset, offset + batch - 1)
                    .execute()
                )
                if not result.data:
                    break
                all_rows.extend(result.data)
                if len(result.data) < batch:
                    break
                offset += batch

            docs = {}
            for row in all_rows:
                doc_id = row["document_id"]
                if doc_id not in docs:
                    title = row.get("document", "")
                    title_lower = title.lower()
                    doc_type = "statute" if any(
                        k in title_lower for k in ["act", "constitution", "regulation"]
                    ) else "case_law"
                    docs[doc_id] = {
                        "id": doc_id,
                        "title": title,
                        "document_type": doc_type,
                        "page_count": 0,
                        "source_url": row.get("source_url", ""),
                        "ingested_at": row.get("created_at"),
                        "_chunk_count": 0,
                    }
                docs[doc_id]["_chunk_count"] += 1

            # Use chunk count as a proxy for page_count
            for d in docs.values():
                d["page_count"] = max(1, d["_chunk_count"] // 3)
                del d["_chunk_count"]

            return [SourceDocument(**d) for d in docs.values()]
        except Exception as e:
            logger.error(f"list_documents error: {e}")
            return []

    async def get_chunk(self, chunk_id: str) -> Optional[SourceContext]:
        try:
            result = (
                self.client.table("document_chunks")
                .select("id, document, section, page, chunk_text")
                .eq("id", chunk_id)
                .limit(1)
                .execute()
            )
            if not result.data:
                return None
            row = result.data[0]
            return SourceContext(
                chunk_id=row["id"],
                document=row["document"],
                section=row["section"],
                page=row["page"],
                chunk_text=row["chunk_text"],
            )
        except Exception:
            return None

    async def close(self):
        """No-op for Supabase — HTTP client is stateless."""
        pass
