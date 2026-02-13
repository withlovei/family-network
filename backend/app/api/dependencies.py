"""
Dependencies for API routes.
"""
from fastapi import HTTPException, Request

from app.codes import AUTH_NOT_AUTHENTICATED


async def get_current_user_id(request: Request) -> str:
    """Get current user ID from request state (set by AuthMiddleware)."""
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail={"code": AUTH_NOT_AUTHENTICATED})
    return user_id
