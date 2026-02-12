from fastapi import FastAPI

from app.api import user_person as user_person_api


def register_user_person_routes(app: FastAPI) -> None:
    """Register user-person mapping routes."""
    app.include_router(user_person_api.router, prefix="/api")

