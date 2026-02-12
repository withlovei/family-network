from fastapi import FastAPI

from app.api import lineages as lineages_api


def register_lineage_routes(app: FastAPI) -> None:
    """Register lineage-related routes."""
    app.include_router(lineages_api.router, prefix="/api")

