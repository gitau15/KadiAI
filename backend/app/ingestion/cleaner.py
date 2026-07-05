import re


def clean_text(text: str) -> str:
    """Normalize extracted text: fix line breaks, remove artifacts, collapse whitespace."""
    # Fix hyphenated line breaks (word-\nword → wordword)
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Collapse 3+ newlines into 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Common OCR artifacts
    text = re.sub(r"Artic1e", "Article", text)
    text = re.sub(r"Sect1on", "Section", text)
    text = re.sub(r"Regu1ation", "Regulation", text)
    text = re.sub(r"E1ection", "Election", text)

    # Remove page number lines (standalone digits)
    text = re.sub(r"^\d{1,4}$\n", "", text, flags=re.MULTILINE)

    # Remove excessive spaces but preserve paragraph breaks
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r" \n", "\n", text)
    text = re.sub(r"\n ", "\n", text)

    # Strip leading/trailing whitespace per line
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines)

    return text.strip()
