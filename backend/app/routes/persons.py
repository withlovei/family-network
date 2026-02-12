from fastapi import FastAPI

from app.api import persons as persons_api


def register_person_routes(app: FastAPI) -> None:
    """Register person-related routes."""
    app.include_router(persons_api.router, prefix="/api")

