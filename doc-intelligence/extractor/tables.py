"""
Table extraction pipeline.
- pdfplumber  → native table detection for born-digital PDFs
- img2table   → table detection from images / scanned pages (optional)
"""
from __future__ import annotations

import io
import logging
from pathlib import Path

from .schema import Table

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# PDF tables via pdfplumber
# ---------------------------------------------------------------------------

def extract_tables_from_pdf(file_bytes: bytes) -> list[Table]:
    import pdfplumber

    tables: list[Table] = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            for tbl_idx, raw_table in enumerate(page.extract_tables(), start=1):
                if not raw_table:
                    continue
                # Normalise cell values
                cleaned = [
                    [str(cell).strip() if cell is not None else "" for cell in row]
                    for row in raw_table
                ]
                if not cleaned:
                    continue
                headers = cleaned[0]
                rows = cleaned[1:]
                tables.append(
                    Table(
                        page=page_num,
                        index=tbl_idx,
                        headers=headers,
                        rows=rows,
                    )
                )
    return tables


# ---------------------------------------------------------------------------
# Image tables via img2table (optional dependency)
# ---------------------------------------------------------------------------

def extract_tables_from_image(file_bytes: bytes, filename: str) -> list[Table]:
    """Attempt table extraction from an image using img2table (if installed)."""
    try:
        from img2table.document import Image as Img2TableImage
        from img2table.ocr import EasyOCR as Img2EasyOCR
    except ImportError:
        logger.info("img2table not installed; skipping image table extraction.")
        return []

    try:
        ocr = Img2EasyOCR(lang=["en"])
        doc = Img2TableImage(src=file_bytes)
        result = doc.extract_tables(ocr=ocr, implicit_rows=True, borderless_tables=False)
        tables: list[Table] = []
        for tbl_idx, (_, tbl) in enumerate(result.items(), start=1):
            df = tbl.df
            if df is None or df.empty:
                continue
            headers = [str(c) for c in df.columns.tolist()]
            rows = [[str(v) for v in row] for row in df.values.tolist()]
            tables.append(
                Table(page=1, index=tbl_idx, headers=headers, rows=rows)
            )
        return tables
    except Exception as exc:
        logger.warning("img2table extraction failed: %s", exc)
        return []


# ---------------------------------------------------------------------------
# Unified entry-point
# ---------------------------------------------------------------------------

def extract_tables(file_bytes: bytes, filename: str) -> list[Table]:
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        return extract_tables_from_pdf(file_bytes)
    elif suffix in {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".webp"}:
        return extract_tables_from_image(file_bytes, filename)
    return []
