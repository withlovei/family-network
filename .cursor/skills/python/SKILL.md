---
name: python-backend
description: Build and modify Python backends with FastAPI, SQLAlchemy, Pydantic, and async patterns. Use when working on Python APIs, FastAPI routes, database models, migrations, auth, or when the user mentions Python backend, FastAPI, or API.
---

# Python Backend Skill

## When to Use

Apply this skill when:
- Adding or editing FastAPI routes, dependencies, or middleware
- Defining or changing SQLAlchemy models and migrations (Alembic)
- Writing Pydantic schemas (request/response)
- Implementing auth (JWT, password hash), services, or config
- Debugging async, DB connection, or validation issues

## Project Structure (Preferred)

```
app/
  main.py         # FastAPI app, CORS, router includes
  config.py       # Pydantic Settings (env), get_settings()
  database.py     # Async engine, session factory, get_db(), Base
  api/            # APIRouter modules (auth, users, ...)
  models/         # SQLAlchemy declarative models
  schemas/        # Pydantic models (request/response)
  services/       # Business logic (auth, etc.)
  middleware/     # Starlette/FastAPI middleware
alembic/          # Migrations (env.py, versions/)
```

## FastAPI

- Route: `@router.get/post/...`; use `async def` for handlers that do I/O.
- Depends: `Depends(get_db)`, `Depends(get_current_user)`; inject session or user.
- Response: return Pydantic model or dict; use `response_model` on router or route.
- Errors: `raise HTTPException(status_code=..., detail="...")`; avoid raw Response unless needed.
- Prefix: mount routers with `app.include_router(router, prefix="/api")`.

## Database (SQLAlchemy 2 + Async)

- Engine: `create_async_engine(url)` with `asyncpg` driver (`postgresql+asyncpg://...`).
- Session: `async_sessionmaker(..., class_=AsyncSession)`; no auto-commit in dependency.
- Model: `class X(Base):` with `Mapped[...]`, `mapped_column(...)`; `DeclarativeBase` for Base.
- In route: `async with AsyncSessionLocal() as session:` or yield from `get_db()`; commit in route or service when needed; rollback on exception.
- Queries: `select(Model).where(...)`; `await session.execute(...)`; `result.scalar_one_or_none()` / `scalars().all()`.

## Pydantic

- Config: use `pydantic-settings` `BaseSettings`; read from env (`.env`); `model_config = ConfigDict(env_file=".env")` or `class Config: env_file = ".env"`.
- Schemas: separate Create/Update/Response; use `EmailStr` for email; `from_attributes = True` for ORM response.
- Validation: rely on Pydantic validators; keep business rules in services when they involve DB or external calls.

## Auth (JWT + Password)

- Hash: `passlib` with bcrypt; hash on register; verify on login.
- Token: create with `jose` (exp, sub, email, role); verify in middleware or dependency; put `user_id`/`role` on `request.state` or return from dependency.
- Middleware: check `Authorization: Bearer <token>` for protected paths; skip for `/auth/login`, `/auth/register`, `/health`.
- Never log or return raw password or token.

## Migrations (Alembic)

- Create revision: `alembic revision -m "description"`; implement `upgrade()` and `downgrade()`.
- Use `op.create_table`, `op.add_column`, etc.; for enums use `sa.Enum(..., name="...")` and create/drop type in downgrade if needed.
- Run: `alembic upgrade head`; ensure `env.py` uses same DB URL as app (sync URL for Alembic if using sync engine in env, or async with run_sync).

## Async

- Use `async def` for route handlers and service functions that await DB or HTTP.
- One event loop; avoid blocking calls in async code (use `run_in_executor` if necessary).
- `get_db`: async generator that yields session; no commit inside dependency unless by design.

## Checklist Before Submitting

- [ ] Type hints on function args and return
- [ ] No `any`; use `Optional[T]`, `Union`, or concrete types
- [ ] Config and secrets from env (pydantic-settings), not hardcoded
- [ ] Passwords hashed; JWT with expiry; auth middleware/dependency applied to protected routes
- [ ] New tables/columns via Alembic migration, not ad-hoc SQL
