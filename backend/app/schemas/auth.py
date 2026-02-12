from pydantic import BaseModel
from app.schemas.user import UserResponse, Token


class LoginResponse(BaseModel):
    user: UserResponse
    token: Token
