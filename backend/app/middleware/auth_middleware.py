from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.codes import AUTH_NOT_AUTHENTICATED, AUTH_INVALID_OR_EXPIRED_TOKEN
from app.services.auth import decode_token


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if (
            request.url.path.startswith("/api/auth/login")
            or request.url.path.startswith("/api/auth/register")
            or request.url.path == "/health"
        ):
            return await call_next(request)
        if request.url.path.startswith("/api/") and request.method != "OPTIONS":
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return JSONResponse(
                    status_code=401,
                    content={"code": AUTH_NOT_AUTHENTICATED},
                )
            token = auth_header.split(" ")[1]
            payload = decode_token(token)
            if not payload:
                return JSONResponse(
                    status_code=401,
                    content={"code": AUTH_INVALID_OR_EXPIRED_TOKEN},
                )
            request.state.user_id = payload.get("sub")
            request.state.user_email = payload.get("email")
            request.state.user_role = payload.get("role")
        return await call_next(request)
