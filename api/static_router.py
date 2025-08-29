import os

from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "..", "static")


@router.get("/")
async def root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))
