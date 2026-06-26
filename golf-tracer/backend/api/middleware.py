from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse


async def error_handler(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal server error: {str(exc)}"},
        )
