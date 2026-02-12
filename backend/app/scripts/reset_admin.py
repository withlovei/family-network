"""
Reset admin password to match ADMIN_EMAIL and ADMIN_PASSWORD from .env.
Run from repo root: ./reset-admin.sh
Or from backend: python -m app.scripts.reset_admin
"""
import asyncio
import sys

from app.config import get_settings
from app.database import AsyncSessionLocal
from app.services.auth import reset_admin_password


def _truncate_password(pwd: str, max_bytes: int = 72) -> str:
    pwd = (pwd or "").strip()
    if len(pwd.encode("utf-8")) <= max_bytes:
        return pwd
    return pwd.encode("utf-8")[:max_bytes].decode("utf-8", errors="ignore")


async def main() -> None:
    settings = get_settings()
    if not settings.admin_email or not settings.admin_password:
        print("Error: Set ADMIN_EMAIL and ADMIN_PASSWORD in backend/.env", file=sys.stderr)
        sys.exit(1)
    email = settings.admin_email.strip()
    password = _truncate_password(settings.admin_password)
    async with AsyncSessionLocal() as session:
        try:
            user = await reset_admin_password(
                session,
                email=email,
                password=password,
                full_name="Admin",
            )
            await session.commit()
            print(f"OK: Admin password reset for {user.email} (id={user.id})")
        except Exception as e:
            await session.rollback()
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
