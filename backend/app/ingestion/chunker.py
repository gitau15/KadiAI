import uuid
from langchain_text_splitters import RecursiveCharacterTextSplitter
import tiktoken

from app.core.config import settings


_tokenizer = None


def _get_tokenizer():
    global _tokenizer
    if _tokenizer is None:
        _tokenizer = tiktoken.get_encoding("cl100k_base")
    return _tokenizer


def chunk_text(
    text: str,
    sections: list[dict],
    doc_name: str,
) -> list[dict]:
    """
    Split text into chunks while respecting section boundaries.
    Returns list of chunk dicts with metadata.
    """
    tokenizer = _get_tokenizer()

    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name=tokenizer.name,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    raw_chunks = splitter.split_text(text)
    doc_id = doc_name.replace(".pdf", "").replace(" ", "_").lower()
    ns = uuid.uuid5(uuid.NAMESPACE_DNS, doc_id)

    chunks = []
    for i, chunk_text in enumerate(raw_chunks):
        current_section = _find_section(chunk_text, sections, text)

        chunks.append(
            {
                "chunk_id": str(uuid.uuid5(ns, f"chunk_{i}")),
                "chunk_index": i,
                "chunk_text": chunk_text,
                "document": doc_name,
                "section": current_section.get("title", ""),
                "page": _estimate_page(i, len(raw_chunks)),
                "document_id": doc_id,
                "source_url": "",
            }
        )

    return chunks


def _find_section(chunk_text: str, sections: list[dict], full_text: str) -> dict:
    """Find the most relevant section for this chunk."""
    # Simple approach: find the last section that starts before this chunk in the full text
    idx = full_text.find(chunk_text)
    if idx < 0:
        return {}

    best = {}
    for s in sections:
        # Estimate section position from line_index
        lines = full_text[:idx].count("\n")
        if s.get("line_index", 0) <= lines:
            best = s

    return best


def _estimate_page(chunk_idx: int, total_chunks: int, total_pages: int = 0) -> int:
    """Estimate page number from chunk position."""
    if total_pages == 0:
        total_pages = max(1, total_chunks // 3)
    return max(1, int((chunk_idx / total_chunks) * total_pages))
