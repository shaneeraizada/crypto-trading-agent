# ============================================================================
# src/api/middleware/auth.py
# ============================================================================
"""Authentication middleware."""

from typing import Callable
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from config.settings import settings


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware."""
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Process request through authentication."""
        
        # Skip auth for health checks and docs
        if request.url.path in ["/health", "/ready", "/", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Skip auth in debug mode
        if settings.debug:
            return await call_next(request)
        
        # Check API key if configured
        if settings.api_key:
            api_key = request.headers.get("X-API-Key")
            if not api_key or api_key != settings.api_key:
                return JSONResponse(
                    status_code=401,
                    content={"error": {"code": "INVALID_API_KEY", "message": "Invalid API key"}}
                )
        
        return await call_next(request)