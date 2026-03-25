"""PDF text extraction using pdfplumber."""
from __future__ import annotations
import re
import unicodedata


class ScannedPDFError(Exception):
    """Raised when a PDF contains no extractable text (image-only)."""


def _normalize(text: str) -> str:
    """Normalize full-width characters and strip control characters."""
    # Full-width → ASCII
    text = unicodedata.normalize("NFKC", text)
    # Strip null bytes and other control chars except newlines/tabs
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    return text


# Section headers to scan for in large documents
TARGET_HEADERS = [
    "設備閾值", "健康度", "閾值",
    "診斷說明", "診斷結果", "診斷",
    "改善建議", "建議", "改善措施",
]

MAX_PAGES_DEFAULT = 50


def extract_text(pdf_bytes: bytes) -> dict:
    """
    Extract raw text from a PDF.

    Returns:
        {
            "raw_text": str,
            "page_count": int,
            "truncated": bool,   # True if doc was very long and clipped
        }

    Raises:
        ScannedPDFError: if no text could be extracted (scanned/image PDF).
        ValueError: if pdf_bytes is not a valid PDF.
    """
    import pdfplumber
    import io

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        page_count = len(pdf.pages)
        pages_text: list[str] = []

        # For large PDFs, always include pages with target headers
        if page_count > MAX_PAGES_DEFAULT:
            # First pass: identify pages containing target section headers
            priority_pages: set[int] = set()
            for i, page in enumerate(pdf.pages):
                raw = page.extract_text(layout=True) or ""
                if any(h in raw for h in TARGET_HEADERS):
                    priority_pages.add(i)

            # Include first 30 pages + priority pages
            pages_to_extract = sorted(set(range(min(30, page_count))) | priority_pages)
            truncated = len(pages_to_extract) < page_count
        else:
            pages_to_extract = list(range(page_count))
            truncated = False

        for i in pages_to_extract:
            page = pdf.pages[i]
            text = page.extract_text(layout=True) or ""
            pages_text.append(f"\n--- PAGE {i + 1} ---\n{text}")

    raw_text = _normalize("\n".join(pages_text)).strip()

    if not raw_text or len(raw_text) < 20:
        raise ScannedPDFError(
            "無法從此 PDF 擷取文字。此 PDF 可能為掃描影像檔，目前尚不支援 OCR 處理。"
        )

    return {
        "raw_text": raw_text,
        "page_count": page_count,
        "truncated": truncated,
    }
