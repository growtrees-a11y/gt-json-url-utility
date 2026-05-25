"""
PROJ-01: JSON & URL Utility Web Suite — FastAPI backend.
Phase 0: Entry points + file structures.
Phase 1: Strict error handling for malformed JSON.
Phase 2: Test suite (5 valid + 5 malformed).
Phase 3: Frontend with ad scaffolding.
"""
import json
import urllib.parse
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="PROJ-01: JSON & URL Utility", version="1.0.0")


class JSONPayload(BaseModel):
    raw: str


class URLPayload(BaseModel):
    url: str


class FormattedResponse(BaseModel):
    success: bool
    data: Any = None
    error: str | None = None
    error_line: int | None = None
    timestamp: str


@app.post("/json/format", response_model=FormattedResponse)
async def format_json(payload: JSONPayload):
    """Format/validate JSON, return line-number errors on failure."""
    ts = datetime.now(timezone.utc).isoformat()
    try:
        parsed = json.loads(payload.raw)
        formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
        return FormattedResponse(success=True, data=formatted, timestamp=ts)
    except json.JSONDecodeError as e:
        return FormattedResponse(
            success=False,
            error=f"JSONDecodeError: {e.msg}",
            error_line=e.lineno,
            timestamp=ts,
        )


@app.post("/url/decode", response_model=FormattedResponse)
async def decode_url(payload: URLPayload):
    """Decode URL-encoded string."""
    ts = datetime.now(timezone.utc).isoformat()
    try:
        decoded = urllib.parse.unquote(payload.url)
        return FormattedResponse(success=True, data=decoded, timestamp=ts)
    except Exception as e:
        return FormattedResponse(success=False, error=str(e), timestamp=ts)


@app.post("/url/encode", response_model=FormattedResponse)
async def encode_url(payload: URLPayload):
    """Encode string to URL-safe format."""
    ts = datetime.now(timezone.utc).isoformat()
    try:
        encoded = urllib.parse.quote(payload.url, safe="")
        return FormattedResponse(success=True, data=encoded, timestamp=ts)
    except Exception as e:
        return FormattedResponse(success=False, error=str(e), timestamp=ts)


@app.post("/json/parse", response_model=FormattedResponse)
async def parse_json(payload: JSONPayload):
    """Parse and return structured JSON with metadata."""
    ts = datetime.now(timezone.utc).isoformat()
    try:
        parsed = json.loads(payload.raw)
        size = len(payload.raw)
        keys = len(parsed) if isinstance(parsed, dict) else 0
        return FormattedResponse(
            success=True,
            data={"parsed": parsed, "size_bytes": size, "top_level_keys": keys},
            timestamp=ts,
        )
    except json.JSONDecodeError as e:
        return FormattedResponse(
            success=False,
            error=f"JSONDecodeError: {e.msg}",
            error_line=e.lineno,
            timestamp=ts,
        )


@app.get("/health")
async def health():
    return {"status": "ok", "project": "PROJ-01", "version": "1.0.0"}
