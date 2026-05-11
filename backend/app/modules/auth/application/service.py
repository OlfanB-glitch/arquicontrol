from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import create_access_token, decode_access_token, hash_password, verify_password
from app.modules.auth.domain.models import AuthResponse, LoginRequest, RegisterRequest, UserResponse
from app.modules.auth.infrastructure.repository import AuthRepository
from app.shared.common import generate_id, utc_now_iso


bearer_scheme = HTTPBearer(auto_error=False)


class AuthService:
    def __init__(self, repository: AuthRepository):
        self.repository = repository

    async def login(self, payload: LoginRequest) -> AuthResponse:
        user = await self.repository.get_by_email(payload.email.lower())
        if not user or not verify_password(payload.password, user["passwordHash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
            )

        access_token = create_access_token(user["id"])
        return AuthResponse(token=access_token, user=UserResponse(**self._sanitize(user)))

    async def register(self, payload: RegisterRequest) -> AuthResponse:
        existing = await self.repository.get_by_email(payload.email.lower())
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una cuenta registrada con este correo electrónico",
            )

        now = utc_now_iso()
        user = {
            "id": f"usr-{generate_id()}",
            "nombreCompleto": payload.nombreCompleto.strip(),
            "email": payload.email.lower(),
            "passwordHash": hash_password(payload.password),
            "rol": "ARQUITECTA_ADMIN",
            "estado": "ACTIVO",
            "createdAt": now,
            "updatedAt": now,
        }

        await self.repository.insert_one(user)

        access_token = create_access_token(user["id"])
        return AuthResponse(token=access_token, user=UserResponse(**self._sanitize(user)))

    async def get_current_user(self, user_id: str) -> UserResponse:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado",
            )
        return UserResponse(**self._sanitize(user))

    @staticmethod
    def _sanitize(user: dict) -> dict:
        cleaned_user = dict(user)
        cleaned_user.pop("passwordHash", None)
        return cleaned_user


auth_service = AuthService(AuthRepository())


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> UserResponse:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión requerida",
        )

    payload = decode_access_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )
    return await auth_service.get_current_user(user_id)