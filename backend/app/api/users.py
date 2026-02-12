from fastapi import APIRouter, Depends, Request
from app.schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=dict)
async def get_current_user(request: Request):
    return {
        "id": request.state.user_id,
        "email": request.state.user_email,
        "role": request.state.user_role,
    }
