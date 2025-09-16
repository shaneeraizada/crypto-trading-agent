# ============================================================================
# src/api/middleware/rate_limiting.py
# ============================================================================
"""Rate limiting middleware."""

import time
from typing import Callable, Dict
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.data.storage.cache.redis_cache import cache


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""
    
    def __init__(self, app, requests_per_minute: int = 100):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.window_size = 60  # 1 minute window
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Process request through rate limiting."""
        
        # Get client identifier
        client_ip = request.client.host if request.client else "unknown"
        user_id = request.headers.get("X-User-ID", client_ip)
        
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/ready"]:
            return await call_next(request)
        
        # Check rate limit
        rate_limit_key = f"rate_limit:{user_id}"
        current_requests = await cache.get_rate_limit_count("api", rate_limit_key)
        
        if current_requests >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": f"Rate limit of {self.requests_per_minute} requests per minute exceeded",
                        "retry_after": self.window_size
                    }
                }
            )
        
        # Increment rate limit counter
        await cache.incr_rate_limit("api", rate_limit_key, self.window_size)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(self.requests_per_minute - current_requests - 1)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + self.window_size)
        
        return response


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "src.api.app:app",
        host=settings.api_host,
        port=settings.api_port,
        workers=settings.api_workers,
        reload=settings.debug,
        log_level=settings.monitoring.log_level.lower()
    )
        