import enum
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserRoleEnum(enum.Enum):
    ADMIN = "admin"
    RECRUITER = "recruiter"


class UserBase(BaseModel):
    email: EmailStr


class UserAuth(UserBase):
    password: str


class UserRegisterRequset(UserBase):
    name: str
    password: str


class UserResponse(UserBase):
    id: UUID
    role: UserRoleEnum
    created_at: datetime


class UserInDB(UserBase):
    id: UUID
    role: UserRoleEnum
    password_hash: str
    created_at: datetime
