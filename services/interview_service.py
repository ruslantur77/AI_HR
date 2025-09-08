from datetime import datetime
from uuid import UUID

from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from exceptions import AlreadyExistsError
from models import InterviewOrm
from schemas import (
    InterviewResponse,
    InterviewResultEnum,
)


class InterviewService:

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def create(
        self,
        resume_id: UUID,
        result: InterviewResultEnum = InterviewResultEnum.PENDING,
        feedback_hr: str | None = None,
        feedback_candidate: str | None = None,
    ) -> InterviewResponse:
        try:
            async with self.session_factory() as session:
                new_resume = InterviewOrm(
                    resume_id=resume_id,
                    result=result,
                    feedback_hr=feedback_hr,
                    feedback_candidate=feedback_candidate,
                )
                session.add(new_resume)
                await session.commit()
                await session.refresh(new_resume)
                return InterviewResponse.model_validate(
                    new_resume, from_attributes=True
                )
        except IntegrityError as e:
            raise AlreadyExistsError("User already exists") from e

    async def get(self, id: UUID) -> InterviewResponse | None:
        async with self.session_factory() as session:
            result = await session.get(InterviewOrm, id)
            if result is None:
                return None
            return InterviewResponse.model_validate(result, from_attributes=True)

    async def update(
        self,
        id: UUID,
        passed_at: datetime,
        result: InterviewResultEnum,
        feedback_hr: str | None = None,
        feedback_candidate: str | None = None,
    ) -> InterviewResponse | None:
        async with self.session_factory() as session:
            stmt = (
                update(InterviewOrm)
                .where(InterviewOrm.id == id)
                .values(
                    passed_at=passed_at,
                    result=result,
                    feedback_hr=feedback_hr,
                    feedback_candidate=feedback_candidate,
                )
                .returning(InterviewOrm)
            )
            res = await session.execute(stmt)
            updated = res.scalar_one_or_none()
            if updated is None:
                return None

            await session.commit()
            return InterviewResponse.model_validate(updated, from_attributes=True)
