"""POST /api/compare — AI parse + diff two uploaded reports."""
from __future__ import annotations
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from backend.api.dependencies import get_anthropic_client
from backend.api.routes.upload import get_session, _SESSION_CACHE
from backend.models.report import (
    CompareRequest,
    ComparisonResult,
    ExtractedReport,
)
from backend.services.ai_parser import parse_report
from backend.services.diff_engine import compare_reports

router = APIRouter()

# Cache completed comparisons keyed by session_id
_RESULT_CACHE: dict[str, ComparisonResult] = {}


@router.post("/compare", response_model=ComparisonResult)
async def run_comparison(
    body: CompareRequest,
    anthropic_client=Depends(get_anthropic_client),
) -> ComparisonResult:
    # Return cached result if available
    if body.session_id in _RESULT_CACHE:
        return _RESULT_CACHE[body.session_id]

    session = get_session(body.session_id)
    consultant_data = session["consultant"]
    software_data = session["software"]

    # AI-assisted structured extraction
    consultant_parsed = parse_report(consultant_data["raw_text"], anthropic_client)
    software_parsed = parse_report(software_data["raw_text"], anthropic_client)

    # Build warnings if extraction confidence is low
    def _warning(parsed: dict) -> str:
        if parsed["confidence"] < 0.3:
            return "未能從 PDF 中找到標準欄位標題，以下欄位可能為空白。請參考下方原始文字。"
        return ""

    consultant_report = ExtractedReport(
        source="consultant",
        raw_text=consultant_data["raw_text"],
        page_count=consultant_data["page_count"],
        equipment_threshold=consultant_parsed["equipment_threshold"],
        diagnostic_description=consultant_parsed["diagnostic_description"],
        improvement_suggestions=consultant_parsed["improvement_suggestions"],
        extraction_confidence=consultant_parsed["confidence"],
        extraction_warning=_warning(consultant_parsed),
    )

    software_report = ExtractedReport(
        source="software",
        raw_text=software_data["raw_text"],
        page_count=software_data["page_count"],
        equipment_threshold=software_parsed["equipment_threshold"],
        diagnostic_description=software_parsed["diagnostic_description"],
        improvement_suggestions=software_parsed["improvement_suggestions"],
        extraction_confidence=software_parsed["confidence"],
        extraction_warning=_warning(software_parsed),
    )

    # Compute diffs
    field_comparisons, overall_similarity = compare_reports(consultant_parsed, software_parsed)

    result = ComparisonResult(
        id=str(uuid.uuid4()),
        consultant_report=consultant_report,
        software_report=software_report,
        field_comparisons=field_comparisons,
        overall_similarity=overall_similarity,
        created_at=datetime.now(timezone.utc),
    )

    _RESULT_CACHE[body.session_id] = result
    return result


@router.get("/compare/{session_id}", response_model=ComparisonResult)
async def get_comparison(session_id: str) -> ComparisonResult:
    if session_id not in _RESULT_CACHE:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="尚無比對結果，請先執行比對。")
    return _RESULT_CACHE[session_id]
