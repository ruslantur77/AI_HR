import os
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from dependencies import get_interview_service, get_questions_service
from rtc.rtc import create_peer_connection
from schemas import RTCOffer
from services import InterviewQuestionsService
from services.interview_service import InterviewService

router = APIRouter(prefix="/api/interview/rtc", tags=["webrtc"])


ROOT = os.path.dirname(__file__)


@router.post("/offer/{interview_id}")
async def offer(
    offer: RTCOffer,
    interview_id: UUID,
    questions_service: Annotated[
        InterviewQuestionsService, Depends(get_questions_service)
    ],
    interview_service: Annotated[InterviewService, Depends(get_interview_service)],
):
    questions = await questions_service.get_questions(interview_id)
    welcome_text = await questions_service.get_welcome_text(interview_id)
    answer = await create_peer_connection(
        offer.sdp, offer.type, questions, welcome_text, interview_service, interview_id
    )
    return JSONResponse(content=answer)
