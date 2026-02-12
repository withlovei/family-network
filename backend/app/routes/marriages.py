from fastapi import FastAPI

from app.api import marriages as marriages_api


def register_marriage_routes(app: FastAPI) -> None:
    """Register marriage-related routes."""
    app.include_router(marriages_api.router, prefix="/api")

