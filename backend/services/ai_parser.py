"""Structured extraction from PDF raw text — Claude API with rule-based fallback."""
from __future__ import annotations
import json
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
    header_re = "|".join(headers)
    other_re = "|".join(_ALL_HEADERS)
    match = re.search(rf"(?:{header_re})[：:\s]*", text)
    if not match:
        return ""
    start = match.end()
    remaining = text[start:]
    next_section = re.search(rf"(?:{other_re})[：:\s]", remaining)
    if next_section:
        content = remaining[: next_section.start()]
    else:
        content = remaining
    return content.strip()


def _rule_based_parse(raw_text: str) -> dict:
    """Regex / rule-based extraction (fallback when no API key)."""
    results = {}
    found_count = 0

    for field_name, patterns in _FIELD_PATTERNS.items():
        content = _extract_section(raw_text, patterns)
        results[field_name] = content
        if content:
            found_count += 1

    # Fallback for diagnostic_description: content between date line and vibration grade
    if not results["diagnostic_description"]:
        date_match = re.search(r'\d{4}-\d{1,2}-\d{1,2}', raw_text)
        grade_match = re.search(r'[A-D]\s*[_（(]\s*[^）)\n]{1,20}[）)][^\n]{0,60}', raw_text)
        if date_match and grade_match and date_match.end() < grade_match.start():
            line_end = raw_text.find('\n', date_match.end())
            content = raw_text[line_end:grade_match.start()].strip()
            if len(content) > 20:
                results["diagnostic_description"] = content
                found_count += 1

    # Fallback for equipment_threshold: find ISO vibration grade pattern
    if not results["equipment_threshold"]:
        grade_match = re.search(r'[A-D]\s*[_（(]\s*[^）)\n]{1,20}[）)][^\n]{0,60}', raw_text)
        if grade_match:
            results["equipment_threshold"] = grade_match.group(0).strip()
            found_count += 1

    return {**results, "confidence": round(found_count / len(_FIELD_PATTERNS), 2)}


def _claude_parse(raw_text: str, client) -> dict:
    """Use Claude API to intelligently extract structured fields."""
    # Limit input to avoid excessive token usage
    text_snippet = raw_text[:4000] if len(raw_text) > 4000 else raw_text

    prompt = f"""從以下振動分析報告文字中，提取三個欄位的內容。

請以 JSON 格式回應，格式如下：
{{
  "equipment_threshold": "設備振動嚴重等級與健康狀態（如：B 尚可 可長期運轉）",
  "diagnostic_description": "診斷說明的完整內容",
  "improvement_suggestions": "改善建議或維修建議的完整內容"
}}

注意：
- 文字可能來自 OCR，含有雜訊或斷行，請盡量還原原意
- 若某欄位找不到，該欄位回傳空字串
- 只回傳 JSON，不要其他說明

報告文字：
{text_snippet}"""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    text = message.content[0].text.strip()
    # Strip markdown code fences if present
    text = re.sub(r'^```[a-z]*\n?', '', text)
    text = re.sub(r'\n?```$', '', text).strip()

    data = json.loads(text)
    found_count = sum(
        1 for k in ("equipment_threshold", "diagnostic_description", "improvement_suggestions")
        if data.get(k)
    )
    return {
        "equipment_threshold": data.get("equipment_threshold", ""),
        "diagnostic_description": data.get("diagnostic_description", ""),
        "improvement_suggestions": data.get("improvement_suggestions", ""),
        "confidence": round(found_count / 3, 2),
    }


def parse_report(raw_text: str, anthropic_client=None) -> dict:
    """
    Extract three structured fields from raw PDF text.
    Uses Claude API when available, falls back to rule-based extraction.
    """
    if not raw_text or not raw_text.strip():
        return EMPTY_RESULT

    if anthropic_client is not None:
        try:
            return _claude_parse(raw_text, anthropic_client)
        except Exception:
            pass  # Fall through to rule-based

    return _rule_based_parse(raw_text)
