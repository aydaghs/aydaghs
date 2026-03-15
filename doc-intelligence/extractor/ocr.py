"""
OCR pipeline.
- Native PDFs  → pdfplumber (lossless text extraction)
- Scanned PDFs → pdf2image → EasyOCR
- Images       → EasyOCR
"""
from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import Optional

from .schema import PageText

logger = logging.getLogger(__name__)

# Lazy-load heavy deps so Streamlit can import this module fast
_easyocr_reader = None


def _get_ocr_reader(languages: list[str] = None):
    global _easyocr_reader
    if _easyocr_reader is None:
        import easyocr
        langs = languages or ["en"]
        _easyocr_reader = easyocr.Reader(langs, gpu=False, verbose=False)
    return _easyocr_reader


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def _is_scanned_page(page) -> bool:
    """Return True when a pdfplumber page has no extractable text."""
    text = page.extract_text() or ""
    return len(text.strip()) < 20


def extract_text_from_pdf(file_bytes: bytes, ocr_languages: list[str] = None) -> list[PageText]:
    """Extract text from a PDF. Uses native extraction; falls back to OCR page-by-page."""
    import pdfplumber

    pages: list[PageText] = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            native_text = page.extract_text() or ""
            if native_text.strip():
                pages.append(PageText(page=i, text=native_text.strip(), method="native"))
            else:
                # Scanned page — rasterise and OCR
                logger.info("Page %d: no native text, running OCR", i)
                pil_img = page.to_image(resolution=200).original
                ocr_text = _ocr_pil_image(pil_img, ocr_languages)
                pages.append(PageText(page=i, text=ocr_text, method="ocr"))
    return pages


def extract_text_from_image(file_bytes: bytes, ocr_languages: list[str] = None) -> list[PageText]:
    """Extract text from a raster image file (PNG, JPG, TIFF, …)."""
    from PIL import Image

    img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    text = _ocr_pil_image(img, ocr_languages)
    return [PageText(page=1, text=text, method="ocr")]


def _ocr_pil_image(img, ocr_languages: Optional[list[str]] = None) -> str:
    """Run EasyOCR on a PIL Image and return joined text."""
    import numpy as np

    reader = _get_ocr_reader(ocr_languages)
    arr = np.array(img)
    results = reader.readtext(arr, detail=0, paragraph=True)
    return "\n".join(results)


def extract_text(
    file_bytes: bytes,
    filename: str,
    ocr_languages: list[str] = None,
) -> list[PageText]:
    """Unified entry-point: dispatch based on file extension."""
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        return extract_text_from_pdf(file_bytes, ocr_languages)
    elif suffix in {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".webp"}:
        return extract_text_from_image(file_bytes, ocr_languages)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")
