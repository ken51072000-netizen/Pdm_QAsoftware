from __future__ import annotations
from datetime import datetime
from typing import Literal
from pydantic import BaseModel


class ExtractedReport(BaseModel):
    source: Literal["consultant", "software"]
    raw_text: str
    equipment_threshold: str = ""   # 設備閾值/健康度
    diagnostic_description: str = ""  # 診斷說明
    improvement_suggestions: str = ""  # 改善建議
    page_count: int = 0
    extraction_warning: str = ""


class DiffSegment(BaseModel):
    type: Literal["equal", "insert", "delete"]
    text: str


class FieldComparison(BaseModel):
    field_name: str
    field_label_zh: str
    consultant_text: str
    software_text: str
    diff_segments: list[DiffSegment]


class ComparisonResult(BaseModel):
    id: str
    consultant_report: ExtractedReport
    software_report: ExtractedReport
    field_comparisons: list[FieldComparison]
    created_at: datetime


class UploadResponse(BaseModel):
    session_id: str
    consultant_page_count: int
    software_page_count: int


class CompareRequest(BaseModel):
    session_id: str
