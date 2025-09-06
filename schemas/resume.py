from __future__ import annotations

import enum
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AutoScreeningStatusEnum(enum.Enum):
    PENDING = "pending"
    ERROR = "error"
    PASSED = "passed"
    REJECTED = "rejected"


class ResumeCreate(BaseModel):
    candidate_id: UUID
    vacancy_id: UUID
    file_path: str


class ResumePlain(ResumeCreate):
    id: UUID
    auto_screening_status: AutoScreeningStatusEnum
    created_at: datetime
