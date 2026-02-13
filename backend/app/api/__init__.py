from fastapi import FastAPI

from app.api import auth, users, networks, families, members, marriages


def register_routes(app: FastAPI) -> None:
    """Register all API routers on the FastAPI app."""
    app.include_router(auth.router, prefix="/api")
    app.include_router(users.router, prefix="/api")
    app.include_router(networks.router, prefix="/api")
    app.include_router(families.router, prefix="/api")
    app.include_router(members.router, prefix="/api")
    app.include_router(marriages.router, prefix="/api")
