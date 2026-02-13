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

---

## Project Structure (Preferred)

```
app/
  main.py           # FastAPI app, lifespan, CORS, router registration
  config.py         # Pydantic Settings (env), get_settings() (cached)
  database.py       # Async engine, session factory, get_db(), Base
  api/              # APIRouter modules by domain (auth, users, ...)
  models/           # SQLAlchemy declarative models (one file per entity or domain)
  schemas/          # Pydantic request/response (Create, Update, Response per entity)
  services/         # Business logic; no HTTP or request objects here
  middleware/       # Starlette/FastAPI middleware (auth, logging)
alembic/            # Migrations (env.py, versions/)
```

**Layering:** Routes (api/) only validate input, call services, and return schemas. Business rules and DB access live in services/; models define data only. Keep dependencies one-way: api → services → models (and config/database).

---

## FastAPI

- **Handlers:** Use `async def` for any route that does I/O (DB, HTTP, file).
- **Routers:** One `APIRouter` per domain with `prefix` and `tags`; mount all with `app.include_router(router, prefix="/api")`.
- **Dependencies:** `Depends(get_db)`, `Depends(get_current_user)` (or similar); inject session and auth; keep handlers thin.
- **Response:** Return Pydantic models or dict; set `response_model` on route or router for docs and validation.
- **Errors:** Use `raise HTTPException(status_code=..., detail="...")` with **user-friendly** messages; avoid exposing internal errors or stack traces in `detail`. Use consistent status codes (400 validation, 401 unauthenticated, 403 forbidden, 404 not found, 409 conflict).
- **Lifespan:** Use `lifespan` for startup/shutdown (e.g. ensure default admin, dispose engine); avoid global state where possible.

---

## Layering & Consistency

- **API layer:** Parse request (Pydantic), call one or more service functions, commit only when the use case succeeds, then return a schema. Do not put business logic or complex queries in the route.
- **Service layer:** Pure business logic; accept `AsyncSession` and domain types/schemas; raise domain-friendly errors or return values; no `request` or `Response`. Reusable across routes and scripts.
- **Naming:** Routers and files by domain (auth, users, persons). Schemas: `XxxCreate`, `XxxUpdate`, `XxxResponse`; services: verb-first (`create_user`, `get_user_by_email`).
- **Single responsibility:** One route handler per operation; extract shared logic into dependencies or services.

---

## Database (SQLAlchemy 2 + Async)

- **Engine:** `create_async_engine(url)` with `asyncpg` (`postgresql+asyncpg://...`); set `echo` from config in development only.
- **Session:** `async_sessionmaker(..., class_=AsyncSession, expire_on_commit=False)`; provide session via `get_db()` that yields and closes; **do not commit** inside `get_db`; rollback and re-raise on exception.
- **Models:** `class X(Base):` with `Mapped[...]`, `mapped_column(...)`; use `DeclarativeBase` for Base. Prefer explicit types and foreign keys; use enums for status/role when appropriate.
- **Queries:** Use `select(Model).where(...)`; `await session.execute(...)`; `result.scalar_one_or_none()` / `result.scalars().all()`. Prefer one query per use case when readable; avoid N+1 (e.g. use options for relationships).
- **Transactions:** Commit in the route or in the service after a full use case; one logical operation = one transaction where possible.

---

## Pydantic

- **Config:** Use `pydantic-settings` `BaseSettings`; load from env (`.env`); use `model_config = ConfigDict(env_file=".env", extra="ignore")` or `class Config`; cache with `@lru_cache def get_settings()` so env is read once.
- **Schemas:** Separate Create / Update / Response; use `EmailStr` for email; use `model_config = ConfigDict(from_attributes=True)` for ORM → response. Keep request schemas slim; put computed or internal fields only in response.
- **Validation:** Use Pydantic validators for format and range; keep rules that need DB or external calls in services and raise `HTTPException` from the route.
- **Naming:** Match API contract (snake_case in JSON); use `alias` or `serialization_alias` only when the API requires different names.

---

## Auth (JWT + Password)

- **Password:** Hash with `passlib` (bcrypt); hash on register and when changing password; never store or log plain password. Handle bcrypt 72-byte limit if accepting very long passwords.
- **Token:** Create with `python-jose` (exp, sub, email, role); verify in middleware or dependency; set `user_id` / `user_email` / `user_role` on `request.state` or return from dependency. Use expiry from config (`ACCESS_TOKEN_EXPIRE_MINUTES`).
- **Middleware:** Validate `Authorization: Bearer <token>` on protected paths; skip for `/api/auth/login`, `/api/auth/register`, `/health`, and other public routes. Return 401 with a clear message when missing or invalid.
- **Secrets:** Secret key and algorithm from config only; never log token or password.

---

## Error Handling & Logging

- **User-facing:** `HTTPException(detail="...")` with short, clear messages (e.g. "Email already registered", "Invalid email or password"). Do not leak DB or internal errors.
- **Logging:** Log exceptions and important business events (e.g. login failure, creation of sensitive resources) at appropriate level; never log passwords or tokens. Use structured fields (request id, user id) when available.
- **Consistency:** Use the same status codes for the same situation across the API (e.g. 401 for bad/missing auth, 403 for insufficient permissions, 404 for missing resource).

---

## Migrations (Alembic)

- **Create:** `alembic revision -m "short_description"`; implement `upgrade()` and `downgrade()` so migrations are reversible when possible.
- **Schema changes:** Use `op.create_table`, `op.add_column`, `op.create_index`, etc.; for enums use `sa.Enum(..., name="...")` and create/drop type in downgrade. Ensure `env.py` uses the same DB URL as the app (sync URL if using sync engine in env, or async with `run_sync`).
- **Safety:** Never edit existing migration files that have already been applied; add a new revision. Test upgrade and downgrade on a copy of data before production.

---

## Async

- Use `async def` for route handlers and service functions that perform I/O (DB, HTTP, file).
- Avoid blocking calls in async code; use `run_in_executor` for CPU-heavy or blocking libraries.
- `get_db`: async generator that yields a session, then closes; no commit inside; on exception, rollback and re-raise so the caller can handle.

---

## Best Practices for Maintainability

- **Type hints:** Use on all function parameters and returns; no `any`; use `X | None` or `Optional[X]`, and generic types where it helps.
- **Imports:** Group stdlib, third-party, local; use absolute imports from `app.*`.
- **Workflow:** Follow project rule **workflow-plan-confirm**: plan and get confirmation before implementing non-trivial changes.
- **Tests:** Structure tests to mirror app (e.g. `tests/api/`, `tests/services/`); use test DB or fixtures; mock external services. Prefer one test file per module or feature.

---

## Checklist Before Submitting

- [ ] Type hints on all function args and return; no `any`
- [ ] Config and secrets from env (pydantic-settings); nothing sensitive hardcoded
- [ ] Routes thin: validate → call service → commit (if needed) → return schema
- [ ] Business logic in services; no heavy logic in route handlers
- [ ] Passwords hashed; JWT with expiry; auth middleware/dependency on protected routes
- [ ] HTTPException with user-friendly detail; consistent status codes
- [ ] New tables/columns via Alembic migration; no ad-hoc schema changes in production
- [ ] No logging of passwords or tokens
