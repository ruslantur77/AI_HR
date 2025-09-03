from __future__ import annotations

from .candidate import CandidatePlain
from .resume_resp import ResumeResponse


class CandidateResponse(CandidatePlain):
    resume: "ResumeResponse | None"
