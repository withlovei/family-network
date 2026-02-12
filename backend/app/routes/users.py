from fastapi import FastAPI

from app.api import users as users_api


def register_user_routes(app: FastAPI) -> None:
    """Register user-related routes."""
    app.include_router(users_api.router, prefix="/api")

