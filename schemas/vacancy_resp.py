from .resume_resp import ResumeResponse
from .vacancy import VacancyPlain


class VacancyResponse(VacancyPlain):
    resumes: list[ResumeResponse]
