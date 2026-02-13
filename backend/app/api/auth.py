from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.codes import (
    AUTH_EMAIL_ALREADY_REGISTERED,
    AUTH_INVALID_CREDENTIALS,
    AUTH_LOGGED_OUT,
    AUTH_USER_INACTIVE,
    AUTH_USER_LOCKED,
)
from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.schemas.auth import LoginResponse
from app.models.user import UserStatus
from app.services.auth import (
    get_user_by_email,
    create_user,
    verify_password,
    create_access_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=LoginResponse)
async def register(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    existing = await get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(status_code=400, detail={"code": AUTH_EMAIL_ALREADY_REGISTERED})
    user = await create_user(db, data)
    await db.commit()
    await db.refresh(user)
    token = create_access_token(user.id, user.email, user.role)
    return LoginResponse(
        user=UserResponse.model_validate(user),
        token=Token(access_token=token),
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    data: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_email(db, data.email)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail={"code": AUTH_INVALID_CREDENTIALS})
    if user.status != UserStatus.ACTIVE:
        if user.status == UserStatus.LOCKED:
            raise HTTPException(status_code=403, detail={"code": AUTH_USER_LOCKED})
        raise HTTPException(status_code=403, detail={"code": AUTH_USER_INACTIVE})
    token = create_access_token(user.id, user.email, user.role)
    return LoginResponse(
        user=UserResponse.model_validate(user),
        token=Token(access_token=token),
    )


@router.post("/logout")
async def logout():
    return {"code": AUTH_LOGGED_OUT}
