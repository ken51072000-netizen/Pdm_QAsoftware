"""AI-assisted structured extraction from PDF raw text using Claude API."""
from __future__ import annotations
import json
import logging

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """你是一位專業的結構化資料擷取助理，專門處理繁體中文工業設備頻譜分析報告。
你的任務是從提供的報告原始文字中，精準擷取以下三個欄位。
請只回傳合法的 JSON 格式，不要加入任何 markdown 標記或額外說明文字。

欄位說明：
1. equipment_threshold（設備閾值/健康度）：描述設備閾值或健康度的內容，可能為數值、表格列或描述性文字。
2. diagnostic_description（診斷說明）：描述設備當前狀態分析的段落，通常在「診斷說明」、「診斷結果」等標題下。
3. improvement_suggestions（改善建議）：建議採取的行動措施，通常在「改善建議」、「建議措施」等標題下。

擷取規則：
- 請從報告中逐字擷取原始文字，不要改寫或摘要。
- 若某欄位在報告中不存在，請回傳空字串 ""。
- 請評估擷取的信心程度（0.0 到 1.0）。

回傳 JSON 格式如下：
{
  "equipment_threshold": "<原始文字或空字串>",
  "diagnostic_description": "<原始文字或空字串>",
  "improvement_suggestions": "<原始文字或空字串>",
  "confidence": <0.0 到 1.0 的浮點數>
}"""

EMPTY_RESULT = {
    "equipment_threshold": "",
    "diagnostic_description": "",
    "improvement_suggestions": "",
    "confidence": 0.0,
}


def parse_report(raw_text: str, anthropic_client) -> dict:
    """
    Use Claude to extract three structured fields from raw PDF text.

    Returns a dict with keys:
        equipment_threshold, diagnostic_description, improvement_suggestions, confidence

    On any failure, returns EMPTY_RESULT with confidence=0.0.
    """
    try:
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            temperature=0,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"[報告原始文字開始]\n{raw_text}\n[報告原始文字結束]",
                }
            ],
        )
        content = response.content[0].text.strip()

        # Strip markdown fences if present
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(
                line for line in lines if not line.startswith("```")
            ).strip()

        result = json.loads(content)

        return {
            "equipment_threshold": str(result.get("equipment_threshold", "")),
            "diagnostic_description": str(result.get("diagnostic_description", "")),
            "improvement_suggestions": str(result.get("improvement_suggestions", "")),
            "confidence": float(result.get("confidence", 0.0)),
        }

    except Exception as exc:
        logger.warning("AI extraction failed: %s", exc)
        return EMPTY_RESULT
