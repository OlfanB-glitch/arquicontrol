from pydantic import BaseModel, EmailStr, Field, model_validator


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class RegisterRequest(BaseModel):
    nombreCompleto: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)
    confirmPassword: str = Field(min_length=8, max_length=64)

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirmPassword:
            raise ValueError("Las contraseñas no coinciden")
        return self


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