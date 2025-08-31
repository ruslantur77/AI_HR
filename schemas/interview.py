import enum
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class InterviewResultEnum(enum.Enum):
    PENDING = "pending"
    PASSED = "passed"
    REJECTED = "rejected"


class InterviewCreate(BaseModel):
    resume_id: UUID
    result: InterviewResultEnum
    feedback_hr: str | None
    feedback_candidate: str | None


class InterviewUpdate(BaseModel):
    passed_at: datetime
    result: InterviewResultEnum
    feedback_hr: str | None
    feedback_candidate: str | None


class InterviewResponse(InterviewCreate):
    id: UUID
    created_at: datetime
    passed_at: datetime | None


class InterviewCandidateResponse(BaseModel):
    id: UUID
    result: InterviewResultEnum
    feedback_candidate: str | None
    created_at: datetime
    passed_at: datetime | None
