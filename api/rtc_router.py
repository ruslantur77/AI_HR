import os

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from rtc.rtc import create_peer_connection
from schemas import RTCOffer

router = APIRouter(prefix="/api/stt", tags=["stt"])


ROOT = os.path.dirname(__file__)


@router.post("/offer")
async def offer(offer: RTCOffer):
    answer = await create_peer_connection(offer.sdp, offer.type)
    return JSONResponse(content=answer)
