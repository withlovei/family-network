from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import engine, AsyncSessionLocal
from app.middleware.auth_middleware import AuthMiddleware
from app.api import register_routes
from app.config import get_settings
from app.services.auth import ensure_admin_user


def _http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Return error response with only 'code' for frontend i18n."""
    detail = exc.detail
    if isinstance(detail, dict) and "code" in detail:
        return JSONResponse(status_code=exc.status_code, content={"code": detail["code"]})
    return JSONResponse(status_code=exc.status_code, content={"code": "unknown"})


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
app.add_exception_handler(HTTPException, _http_exception_handler)

app.add_middleware(AuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3008", "http://127.0.0.1:3008"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_routes(app)


@app.get("/health")
async def health():
    return {"status": "ok"}
