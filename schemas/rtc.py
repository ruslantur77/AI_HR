from pydantic import BaseModel


class RTCOffer(BaseModel):
    sdp: str
    type: str
