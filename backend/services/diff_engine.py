"""Text diff engine using diff-match-patch with Chinese-aware tokenization."""
from __future__ import annotations
import re
from diff_match_patch import diff_match_patch

from backend.models.report import DiffSegment, FieldComparison

# Mapping from diff-match-patch op codes to our type strings
_OP_MAP = {-1: "delete", 0: "equal", 1: "insert"}

# Fields to compare (name, Chinese label)
FIELDS = [
    ("equipment_threshold", "設備閾值/健康度"),
    ("diagnostic_description", "診斷說明"),
    ("improvement_suggestions", "改善建議"),
]


def _tokenize_chinese(text: str) -> list[str]:
    """
    Split Chinese text into semantic units for better diff readability.
    Splits on sentence-ending punctuation and newlines.
    """
    if not text:
        return []
    # Split after 。！？；… and newlines, keeping the delimiter with the preceding unit
    parts = re.split(r"(?<=[。！？；…\n])", text)
    return [p for p in parts if p]


def _compute_diff(a: str, b: str) -> list[DiffSegment]:
    """Compute character-level diff between a and b."""
    dmp = diff_match_patch()

    if not a and not b:
        return []

    diffs = dmp.diff_main(a, b)
    dmp.diff_cleanupSemantic(diffs)

    return [
        DiffSegment(type=_OP_MAP[op], text=text)
        for op, text in diffs
        if text
    ]


def compare_reports(consultant: dict, software: dict) -> list[FieldComparison]:
    """
    Compare three fields between consultant and software parsed reports.

    Args:
        consultant: dict with keys equipment_threshold, diagnostic_description, improvement_suggestions
        software:   same structure
    """
    comparisons: list[FieldComparison] = []

    for field_name, label_zh in FIELDS:
        a = consultant.get(field_name, "")
        b = software.get(field_name, "")

        comparisons.append(
            FieldComparison(
                field_name=field_name,
                field_label_zh=label_zh,
                consultant_text=a,
                software_text=b,
                diff_segments=_compute_diff(a, b),
            )
        )

    return comparisons
