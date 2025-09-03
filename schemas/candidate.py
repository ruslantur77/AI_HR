from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class CandidateCreate(BaseModel):
    full_name: str
    email: EmailStr


class CandidatePlain(CandidateCreate):
    id: UUID
    created_at: datetime
