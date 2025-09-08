from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from exceptions import AlreadyExistsError
from models import ResumeOrm
from schemas import (
    AutoScreeningStatusEnum,
    ResumeResponse,
)


class ResumeService:

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def create(
        self, candidate_id: UUID, vacancy_id: UUID, file_path: str
    ) -> ResumeResponse:
        try:
            async with self.session_factory() as session:
                new_resume = ResumeOrm(
                    candidate_id=candidate_id,
                    vacancy_id=vacancy_id,
                    file_path=file_path,
                )
                session.add(new_resume)
                await session.commit()
                await session.refresh(new_resume)
                return ResumeResponse.model_validate(new_resume, from_attributes=True)
        except IntegrityError as e:
            raise AlreadyExistsError("User already exists") from e

    async def get(self, id: UUID) -> ResumeResponse | None:
        async with self.session_factory() as session:
            result = await session.get(ResumeOrm, id)
            if result is None:
                return None
            return ResumeResponse.model_validate(result, from_attributes=True)

    async def get_by_vacancy_id(self, id: UUID) -> list[ResumeResponse]:
        async with self.session_factory() as session:
            stmt = select(ResumeOrm).filter_by(vacancy_id=id)
            result = await session.execute(stmt)
            res = result.scalars().all()
            return [ResumeResponse.model_validate(r, from_attributes=True) for r in res]

    async def update_auto_screening_status(
        self, id: UUID, status: AutoScreeningStatusEnum
    ) -> ResumeResponse:
        async with self.session_factory() as session:
            stmt = (
                update(ResumeOrm)
                .filter_by(id=id)
                .values(auto_screening_status=status)
                .returning(ResumeOrm)
            )
            result = await session.execute(stmt)
            await session.commit()
            res = result.scalar_one()
            return ResumeResponse.model_validate(res, from_attributes=True)
