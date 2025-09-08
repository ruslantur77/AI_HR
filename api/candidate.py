from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from dependencies import get_access_token_data, get_candidate_service
from schemas import AccesTokenData, CandidateResponse
from services import CandidateService

router = APIRouter(prefix="/api/candidate", tags=["candidate"])


@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(
    candidate_id: UUID,
    candidate_service: Annotated[CandidateService, Depends(get_candidate_service)],
    access_token_data: Annotated[AccesTokenData, Depends(get_access_token_data)],
):
    candidate = await candidate_service.get(id=candidate_id)
    return candidate
