"""POST /api/upload — receive two PDFs and extract raw text."""
from __future__ import annotations
import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.models.report import UploadResponse
from backend.services.pdf_extractor import ScannedPDFError, extract_text

router = APIRouter()

# In-memory session cache: session_id -> {consultant: dict, software: dict}
_SESSION_CACHE: dict[str, dict] = {}


def get_session(session_id: str) -> dict:
    data = _SESSION_CACHE.get(session_id)
    if data is None:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' 不存在，請重新上傳檔案。")
    return data


@router.post("/upload", response_model=UploadResponse)
async def upload_pdfs(
    consultant_pdf: UploadFile = File(..., description="人工顧問報告 PDF"),
    software_pdf: UploadFile = File(..., description="軟體系統報告 PDF"),
) -> UploadResponse:
    for f in (consultant_pdf, software_pdf):
        if f.content_type not in ("application/pdf", "application/octet-stream"):
            if not (f.filename or "").lower().endswith(".pdf"):
                raise HTTPException(
                    status_code=400,
                    detail=f"檔案 '{f.filename}' 不是 PDF 格式。請上傳 .pdf 檔案。",
                )

    consultant_bytes = await consultant_pdf.read()
    software_bytes = await software_pdf.read()

    try:
        consultant_data = extract_text(consultant_bytes)
    except ScannedPDFError as e:
        raise HTTPException(status_code=422, detail=f"人工顧問 PDF 錯誤：{e}")
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"無法解析人工顧問 PDF：{e}")

    try:
        software_data = extract_text(software_bytes)
    except ScannedPDFError as e:
        raise HTTPException(status_code=422, detail=f"軟體系統 PDF 錯誤：{e}")
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"無法解析軟體系統 PDF：{e}")

    session_id = str(uuid.uuid4())
    _SESSION_CACHE[session_id] = {
        "consultant": consultant_data,
        "software": software_data,
    }

    return UploadResponse(
        session_id=session_id,
        consultant_page_count=consultant_data["page_count"],
        software_page_count=software_data["page_count"],
    )
