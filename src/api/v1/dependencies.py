# ============================================================================
# src/api/dependencies.py
# ============================================================================
"""FastAPI dependencies."""

from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db as _get_db
from config.settings import settings


async def get_db() -> AsyncSession:
    """Database dependency."""
    async for db in _get_db():
        yield db


async def get_current_user(
    authorization: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """Get current user from authorization header."""
    if not authorization:
        if settings.api_key:
            raise HTTPException(status_code=401, detail="Authorization header required")
        # Return anonymous user for development
        return {"id": "anonymous", "username": "anonymous"}
    
    # For development, we'll accept any authorization
    # In production, implement proper JWT validation
    if authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        # Validate token here
        return {"id": "user123", "username": "testuser"}
    
    raise HTTPException(status_code=401, detail="Invalid authorization header")


async def get_admin_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get current user with admin privileges."""
    # Implement admin check
    if current_user.get("username") != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user
