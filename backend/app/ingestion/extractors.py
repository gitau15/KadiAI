import fitz
import pdfplumber
from pathlib import Path


def extract_text(pdf_path: Path, pdf_type: str) -> str:
    if pdf_type == "digital":
        return _extract_digital(pdf_path)
    return _extract_scanned(pdf_path)


def _extract_digital(pdf_path: Path) -> str:
    """Extract text from digital PDF. Falls back to pdfplumber for table-heavy pages."""
    parts = []
    doc = fitz.open(str(pdf_path))
    try:
        for page in doc:
            text = page.get_text("text")
            if len(text.strip()) < 50:
                # Low-text page — try pdfplumber
                try:
                    with pdfplumber.open(str(pdf_path)) as plumber:
                        if page.number < len(plumber.pages):
                            text = plumber.pages[page.number].extract_text() or ""
                except Exception:
                    pass
            parts.append(text)
    finally:
        doc.close()
    return "\n\n".join(parts)


def _extract_scanned(pdf_path: Path) -> str:
    """OCR scanned PDF using Tesseract."""
    from pdf2image import convert_from_path
    import pytesseract
    images = convert_from_path(str(pdf_path), dpi=300)
    texts = []
    for img in images:
        text = pytesseract.image_to_string(img, lang="eng")
        texts.append(text)
    return "\n\n".join(texts)
