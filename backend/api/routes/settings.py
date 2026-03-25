"""GET/POST /api/settings/api-key — manage Anthropic API key."""
from __future__ import annotations
import os
from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

# .env lives at the project root (one level above backend/)
_ENV_PATH = Path(__file__).parent.parent.parent.parent / ".env"


def _read_env() -> dict[str, str]:
    if not _ENV_PATH.exists():
        return {}
    result: dict[str, str] = {}
    for line in _ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            result[k.strip()] = v.strip().strip("\"'")
    return result


def _write_env(data: dict[str, str]) -> None:
    lines = [f'{k}="{v}"' for k, v in data.items()]
    _ENV_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


class ApiKeyRequest(BaseModel):
    key: str


@router.get("/settings/api-key")
def get_api_key_status() -> dict:
    key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if key:
        preview = key[:8] + "..." + key[-4:]
    else:
        preview = ""
    return {"configured": bool(key), "preview": preview}


@router.post("/settings/api-key")
def save_api_key(body: ApiKeyRequest) -> dict:
    key = body.key.strip()
    if not key:
        return {"success": False, "message": "API Key 不可為空"}

    # Update runtime environment
    os.environ["ANTHROPIC_API_KEY"] = key

    # Persist to .env file
    env_data = _read_env()
    env_data["ANTHROPIC_API_KEY"] = key
    _write_env(env_data)

    return {"success": True, "message": "API Key 已儲存"}


@router.delete("/settings/api-key")
def delete_api_key() -> dict:
    os.environ.pop("ANTHROPIC_API_KEY", None)

    env_data = _read_env()
    env_data.pop("ANTHROPIC_API_KEY", None)
    _write_env(env_data)

    return {"success": True, "message": "API Key 已移除"}
