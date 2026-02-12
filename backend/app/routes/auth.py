from fastapi import FastAPI

from app.api import auth as auth_api


def register_auth_routes(app: FastAPI) -> None:
    """Register auth-related routes."""
    app.include_router(auth_api.router, prefix="/api")

