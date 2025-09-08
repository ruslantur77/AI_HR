import enum
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class VacancyStatusEnum(enum.Enum):
    OPEN = "open"
    CLOSED = "closed"


class VacancyCreate(BaseModel):
    title: str
    description: str


class VacancyPlain(VacancyCreate):
    id: UUID
    status: VacancyStatusEnum
    created_at: datetime
