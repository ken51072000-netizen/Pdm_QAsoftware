"""PDF text extraction using pdfplumber with OCR fallback."""
from __future__ import annotations
import re
import unicodedata


class ScannedPDFError(Exception):
    """Raised when a PDF contains no extractable text and OCR also failed."""


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
        # Fallback to OCR for scanned/image PDFs
        ocr_text = _ocr_pdf(pdf_bytes)
        return {
            "raw_text": ocr_text,
            "page_count": page_count,
            "truncated": truncated,
            "ocr": True,
        }

    return {
        "raw_text": raw_text,
        "page_count": page_count,
        "truncated": truncated,
        "ocr": False,
    }


def _ocr_pdf(pdf_bytes: bytes) -> str:
    """Render PDF pages as images and run Tesseract OCR."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise ScannedPDFError(
            "OCR 需要 PyMuPDF：請執行 pip install pymupdf"
        )
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        raise ScannedPDFError(
            "OCR 需要 pytesseract 與 Pillow：請執行 pip install pytesseract pillow"
        )

    try:
        import io
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        pages_text: list[str] = []

        for i, page in enumerate(doc):
            # Render at 300 DPI (72 DPI default × 300/72 ≈ 4.17)
            mat = fitz.Matrix(300 / 72, 300 / 72)
            pix = page.get_pixmap(matrix=mat)
            img = Image.open(io.BytesIO(pix.tobytes("png")))

            # Traditional Chinese + English
            text = pytesseract.image_to_string(img, lang="chi_tra+eng")
            pages_text.append(f"\n--- PAGE {i + 1} ---\n{text}")

        ocr_text = _normalize("\n".join(pages_text)).strip()
        if not ocr_text or len(ocr_text) < 20:
            raise ScannedPDFError("OCR 未能識別出任何文字，請確認 PDF 影像品質。")
        return ocr_text

    except ScannedPDFError:
        raise
    except Exception as e:
        raise ScannedPDFError(f"OCR 處理失敗：{e}")
