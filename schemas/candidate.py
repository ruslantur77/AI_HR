from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr

from .resume import ResumeResponse


class CandidateCreate(BaseModel):
    full_name: str
    email: EmailStr


class CandidateResponse(CandidateCreate):
    id: UUID
    created_at: datetime
    resume: ResumeResponse | None
