"""
PDF ingestion module.

Handles two kinds of PDFs:
  1. Text-based PDFs  -> extracted directly with PyPDF2 (fast, no deps on
                          poppler/tesseract).
  2. Scanned PDFs      -> pages with little/no extractable text are
                          rasterized (pdf2image) and passed through
                          Tesseract OCR (pytesseract).

Returns a list of dicts: {"source": filename, "page": page_num, "text": text}
so each chunk built downstream can cite its exact source + page.
"""

import os
import logging

from PyPDF2 import PdfReader

try:
    from pdf2image import convert_from_path
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

from config import OCR_FALLBACK_CHAR_THRESHOLD

logger = logging.getLogger(__name__)


def _ocr_page(pdf_path: str, page_number: int) -> str:
    """Rasterize a single PDF page and run Tesseract OCR on it."""
    if not OCR_AVAILABLE:
        logger.warning(
            "OCR requested but pdf2image/pytesseract not installed. "
            "Install poppler-utils + tesseract-ocr on your system, then "
            "`pip install pdf2image pytesseract`."
        )
        return ""

    images = convert_from_path(
        pdf_path, first_page=page_number + 1, last_page=page_number + 1
    )
    if not images:
        return ""
    return pytesseract.image_to_string(images[0])


def load_pdf(pdf_path: str) -> list[dict]:
    """
    Extract text from a single PDF, page by page, with automatic OCR
    fallback for pages that look scanned (little/no extractable text).
    """
    filename = os.path.basename(pdf_path)
    reader = PdfReader(pdf_path)
    pages_out = []

    for page_num, page in enumerate(reader.pages):
        text = (page.extract_text() or "").strip()

        if len(text) < OCR_FALLBACK_CHAR_THRESHOLD:
            logger.info(f"{filename} page {page_num + 1}: falling back to OCR")
            ocr_text = _ocr_page(pdf_path, page_num).strip()
            if ocr_text:
                text = ocr_text

        if text:
            pages_out.append({
                "source": filename,
                "page": page_num + 1,
                "text": text,
            })

    return pages_out


def load_pdf_directory(directory: str) -> list[dict]:
    """Load and extract text from every PDF in a directory."""
    all_pages = []
    for fname in sorted(os.listdir(directory)):
        if fname.lower().endswith(".pdf"):
            path = os.path.join(directory, fname)
            logger.info(f"Loading {fname} ...")
            all_pages.extend(load_pdf(path))
    return all_pages


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "sample_docs"
    pages = load_pdf_directory(target_dir)
    print(f"Extracted {len(pages)} pages from '{target_dir}'")
    for p in pages[:2]:
        print(f"--- {p['source']} (page {p['page']}) ---")
        print(p["text"][:300], "...\n")
