from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserResponse(BaseModel):
    id: str
    nombreCompleto: str
    email: EmailStr
    rol: str
    estado: str
    createdAt: str
    updatedAt: str


class AuthResponse(BaseModel):
    token: str
    user: UserResponse


class UserSeed(BaseModel):
    id: str
    nombreCompleto: str
    email: EmailStr
    passwordHash: str
    rol: str
    estado: str
    createdAt: str
    updatedAt: str