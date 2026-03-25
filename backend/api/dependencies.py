"""FastAPI dependencies."""
from __future__ import annotations
import os
from functools import lru_cache

import anthropic
from fastapi import HTTPException


@lru_cache(maxsize=1)
def get_anthropic_client() -> anthropic.Anthropic:
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="ANTHROPIC_API_KEY 環境變數未設定。請在 backend/.env 中設定您的 API 金鑰。",
        )
    return anthropic.Anthropic(api_key=api_key)
