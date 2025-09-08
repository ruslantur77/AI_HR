from __future__ import annotations

from .candidate import CandidatePlain
from .interview import InterviewResponse
from .resume import ResumePlain
from .vacancy import VacancyPlain


class ResumeResponse(ResumePlain):
    candidate: "CandidatePlain"
    vacancy: "VacancyPlain"
    interview: "InterviewResponse | None"
