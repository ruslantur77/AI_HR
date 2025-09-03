import asyncio
import shutil
from pathlib import Path
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)

from config import config
from dependencies import (
    get_access_token_data,
    get_candidate_service,
    get_interview_service,
    get_resume_service,
)
from schemas import AccesTokenData, CandidateCreate, ResumeResponse
from services import CandidateService, InterviewService, ResumeService
from use_cases import ResumeProcessUseCase

router = APIRouter(prefix="/api/resume", tags=["resume"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/", response_model=ResumeResponse)
async def submit_candidate(
    candidate_service: Annotated[CandidateService, Depends(get_candidate_service)],
    resume_service: Annotated[ResumeService, Depends(get_resume_service)],
    interview_service: Annotated[InterviewService, Depends(get_interview_service)],
    access_token_data: Annotated[AccesTokenData, Depends(get_access_token_data)],
    full_name: str = Form(...),
    email: str = Form(...),
    vacancy_id: UUID = Form(...),
    file: UploadFile = File(...),
) -> ResumeResponse:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file"
        )

    file_ext = Path(file.filename).suffix
    unique_filename = f"{uuid4()}{file_ext}"
    file_location = UPLOAD_DIR / unique_filename

    with file_location.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    candidate_data = CandidateCreate(full_name=full_name, email=email)
    candidate = await candidate_service.create(
        full_name=candidate_data.full_name,
        email=candidate_data.email,
    )

    resume = await resume_service.create(
        candidate_id=candidate.id, vacancy_id=vacancy_id, file_path=str(file_location)
    )

    resume_process_uc = ResumeProcessUseCase(
        resume_service=resume_service,
        interview_service=interview_service,
        api_key=config.OPENROUTER_API_KEY,
    )
    asyncio.create_task(resume_process_uc.execute(resume_id=resume.id))

    return resume


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: UUID,
    resume_service: Annotated[ResumeService, Depends(get_resume_service)],
    access_token_data: Annotated[AccesTokenData, Depends(get_access_token_data)],
):
    res = await resume_service.get(id=resume_id)
    return res


@router.get("/", response_model=list[ResumeResponse])
async def get_resumes(
    resume_service: Annotated[ResumeService, Depends(get_resume_service)],
    access_token_data: Annotated[AccesTokenData, Depends(get_access_token_data)],
    vacancy_id: UUID = Query(..., description="ID вакансии"),
):
    res = await resume_service.get_by_vacancy_id(id=vacancy_id)
    return res
