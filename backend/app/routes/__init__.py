from fastapi import FastAPI

from app.routes.auth import register_auth_routes
from app.routes.users import register_user_routes
from app.routes.user_person import register_user_person_routes
from app.routes.persons import register_person_routes
from app.routes.lineages import register_lineage_routes
from app.routes.marriages import register_marriage_routes
from app.routes.posts import register_post_routes


def register_routes(app: FastAPI) -> None:
    """Register all application routes on the FastAPI app."""
    register_auth_routes(app)
    register_user_routes(app)
    register_user_person_routes(app)
    register_person_routes(app)
    register_lineage_routes(app)
    register_marriage_routes(app)
    register_post_routes(app)

