from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, AsyncSessionLocal
from app.middleware.auth_middleware import AuthMiddleware
from app.api import auth, users, persons, lineages, marriages, posts, user_person
from app.config import get_settings
from app.services.auth import ensure_admin_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    if settings.admin_email and settings.admin_password:
        async with AsyncSessionLocal() as session:
            try:
                user = await ensure_admin_user(
                    session,
                    email=settings.admin_email,
                    password=settings.admin_password,
                    full_name="Admin",
                )
                if user:
                    await session.commit()
            except Exception:
                await session.rollback()
    yield
    await engine.dispose()


app = FastAPI(
    title="Family Network API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(AuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3008", "http://127.0.0.1:3008"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(user_person.router, prefix="/api")
app.include_router(persons.router, prefix="/api")
app.include_router(lineages.router, prefix="/api")
app.include_router(marriages.router, prefix="/api")
app.include_router(posts.router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok"}
