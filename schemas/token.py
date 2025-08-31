from datetime import datetime
from uuid import UUID

from pydantic import UUID4, BaseModel

from .user import UserRoleEnum


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class AccesTokenData(BaseModel):
    user_id: UUID
    role: UserRoleEnum


class RefreshTokenData(BaseModel):
    user_id: UUID
    jti: UUID4


class GeneratedToken(BaseModel):
    token: str
    expiration_time: datetime


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
