from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from dependencies import (
    get_access_token_data,
    get_interview_service,
)
from schemas import AccesTokenData, InterviewCandidateResponse, InterviewResponse
from services import InterviewService

router = APIRouter(prefix="/api/interview", tags=["interview"])


@router.get("/{interview_id}/status", response_model=InterviewCandidateResponse)
async def get_interview_result_candidate(
    interview_id: UUID,
    interview_service: InterviewService = Depends(get_interview_service),
) -> InterviewCandidateResponse:
    res = await interview_service.get(id=interview_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )
    return InterviewCandidateResponse.model_validate(res, from_attributes=True)


@router.get("/{interview_id}", response_model=InterviewResponse)
async def get_interview(
    interview_id: UUID,
    access_token_data: Annotated[AccesTokenData, Depends(get_access_token_data)],
    interview_service: InterviewService = Depends(get_interview_service),
) -> InterviewResponse:
    res = await interview_service.get(id=interview_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )
    return res
