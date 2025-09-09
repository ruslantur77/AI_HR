from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from api import (
    auth_router,
    candidate_router,
    interview_router,
    resume_router,
    vacancy_router,
    webrtc_router,
)
from config import config
from database import create_tables
from exceptions import AppException
from exceptions_handler import exception_handler
from logger import setup_logger
from rtc.rtc import shutdown

setup_logger()


@asynccontextmanager
async def startup_event(app: FastAPI):
    engine = create_async_engine(
        config.DB_URL,
        echo=False,
        pool_size=10,
        max_overflow=20,
        future=True,
    )

    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    await create_tables(engine)
    app.state.session_factory = AsyncSessionLocal
    yield
    await shutdown()


app = FastAPI(
    lifespan=startup_event,
    swagger_ui_parameters={
        "tryItOutEnabled": True,
        "withCredentials": True,
    },
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


app.include_router(webrtc_router)
app.include_router(auth_router)
app.include_router(candidate_router)
app.include_router(vacancy_router)
app.include_router(resume_router)
app.include_router(interview_router)
app.add_exception_handler(AppException, exception_handler)
