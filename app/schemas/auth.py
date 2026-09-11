from pydantic import BaseModel, EmailStr


class GoogleAuthRequest(BaseModel):
    id_token: str


class UserResponse(BaseModel):
    email: str
    name: str | None = None
    picture: str | None = None


class AuthSuccessResponse(BaseModel):
    status: str
    user: UserResponse