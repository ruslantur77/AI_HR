import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api import static_router, webrtc_router
from rtc.rtc import shutdown

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def startup_event(app: FastAPI):
    yield
    await shutdown()


app = FastAPI(
    lifespan=startup_event,
    swagger_ui_parameters={
        "tryItOutEnabled": True,
        "withCredentials": True,
    },
)
app.include_router(webrtc_router)
app.include_router(static_router)
app.mount("/static", StaticFiles(directory="static"), name="static")
