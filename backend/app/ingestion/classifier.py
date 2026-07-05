import fitz  # PyMuPDF
from pathlib import Path


def classify_pdf(pdf_path: Path) -> str:
    """
    Returns 'digital' if the PDF has an extractable text layer,
    'scanned' otherwise (needs OCR).
    """
    doc = fitz.open(str(pdf_path))
    try:
        for page_num in range(min(3, len(doc))):
            text = doc[page_num].get_text().strip()
            if len(text) > 100:
                return "digital"
        return "scanned"
    finally:
        doc.close()
