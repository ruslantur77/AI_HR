import enum
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from .resume import ResumeResponse


class VacancyStatusEnum(enum.Enum):
    OPEN = "open"
    CLOSED = "closed"


class VacancyCreate(BaseModel):
    title: str
    description: str


class VacancyResponse(VacancyCreate):
    id: UUID
    status: VacancyStatusEnum
    created_at: datetime
    resumes: list[ResumeResponse]
