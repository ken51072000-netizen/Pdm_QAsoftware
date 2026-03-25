"""FastAPI dependencies."""
from __future__ import annotations
import os


def get_anthropic_client():
    """Return an Anthropic client if ANTHROPIC_API_KEY is set, else None."""
    key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not key:
        return None
    try:
        import anthropic
        return anthropic.Anthropic(api_key=key)
    except Exception:
        return None
