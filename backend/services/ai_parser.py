"""Rule-based structured extraction from PDF raw text (no API required)."""
from __future__ import annotations
import re


def _spaced(s: str) -> str:
    """Allow optional spaces between each character (handles OCR spacing)."""
    return r"\s*".join(re.escape(c) for c in s)


# Section header patterns mapped to field names
_FIELD_PATTERNS = {
    "equipment_threshold": [
        _spaced("設備閾值"), _spaced("振動嚴重等級"), _spaced("健康度"), _spaced("閾值"),
        _spaced("振動等級"),
    ],
    "diagnostic_description": [
        _spaced("診斷說明"), _spaced("診斷結果"), _spaced("診斷"),
    ],
    "improvement_suggestions": [
        _spaced("改善建議"), _spaced("維修建議"), _spaced("建議措施"), _spaced("改善措施"), _spaced("建議"),
    ],
}

# All known section headers (to detect where a section ends)
_ALL_HEADERS = [
    pattern
    for patterns in _FIELD_PATTERNS.values()
    for pattern in patterns
]

EMPTY_RESULT = {
    "equipment_threshold": "",
    "diagnostic_description": "",
    "improvement_suggestions": "",
    "confidence": 0.0,
}


def _extract_section(text: str, headers: list[str]) -> str:
    """
    Find the first matching header in text and return the content
    that follows it, until the next known section header or end of text.
    """
    header_re = "|".join(headers)
    other_re = "|".join(_ALL_HEADERS)

    # Find the header
    match = re.search(rf"(?:{header_re})[：:\s]*", text)
    if not match:
        return ""

    start = match.end()
    remaining = text[start:]

    # Find where the next section starts
    next_section = re.search(rf"(?:{other_re})[：:\s]", remaining)
    if next_section:
        content = remaining[: next_section.start()]
    else:
        content = remaining

    return content.strip()


def parse_report(raw_text: str, anthropic_client=None) -> dict:
    """
    Extract three structured fields from raw PDF text using keyword matching.

    The anthropic_client parameter is kept for API compatibility but is not used.
    Returns a dict with keys:
        equipment_threshold, diagnostic_description, improvement_suggestions, confidence
    """
    if not raw_text or not raw_text.strip():
        return EMPTY_RESULT

    results = {}
    found_count = 0

    for field_name, patterns in _FIELD_PATTERNS.items():
        content = _extract_section(raw_text, patterns)
        results[field_name] = content
        if content:
            found_count += 1

    # Fallback for diagnostic_description:
    # Extract content between the report date line and the vibration grade line.
    if not results["diagnostic_description"]:
        date_match = re.search(r'\d{4}-\d{1,2}-\d{1,2}', raw_text)
        grade_match = re.search(r'[A-D]\s*[_（(]\s*[^）)\n]{1,20}[）)][^\n]{0,60}', raw_text)
        if date_match and grade_match and date_match.end() < grade_match.start():
            line_end = raw_text.find('\n', date_match.end())
            content = raw_text[line_end:grade_match.start()].strip()
            if len(content) > 20:
                results["diagnostic_description"] = content
                found_count += 1

    # Fallback for equipment_threshold:
    # If no header found, look for ISO vibration grade pattern like "B（尚可）可長期運轉".
    if not results["equipment_threshold"]:
        grade_match = re.search(r'[A-D]\s*[_（(]\s*[^）)\n]{1,20}[）)][^\n]{0,60}', raw_text)
        if grade_match:
            results["equipment_threshold"] = grade_match.group(0).strip()
            found_count += 1

    # Confidence: proportion of fields successfully extracted
    confidence = round(found_count / len(_FIELD_PATTERNS), 2)

    return {**results, "confidence": confidence}
