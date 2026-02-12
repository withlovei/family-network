from fastapi import FastAPI

from app.api import posts as posts_api


def register_post_routes(app: FastAPI) -> None:
    """Register post-related routes."""
    app.include_router(posts_api.router, prefix="/api")

