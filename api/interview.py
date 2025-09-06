from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from dependencies import (
    get_interview_service,
)
from schemas import InterviewCandidateResponse, InterviewResponse
from services import InterviewService

router = APIRouter(prefix="/api/interview", tags=["interview"])


@router.get("/{interview_id}", response_model=InterviewCandidateResponse)
async def get_interview(
    interview_id: UUID,
    interview_service: InterviewService = Depends(get_interview_service),
) -> InterviewResponse:
    res = await interview_service.get(id=interview_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )
    return res
