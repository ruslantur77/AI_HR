from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from exceptions import AlreadyExistsError
from models import CandidateOrm
from schemas import CandidateResponse


class CandidateService:

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def create(self, full_name: str, email: str) -> CandidateResponse:
        try:
            async with self.session_factory() as session:
                new_candidate = CandidateOrm(full_name=full_name, email=email)
                session.add(new_candidate)
                await session.commit()
                await session.refresh(new_candidate)
                return CandidateResponse.model_validate(
                    new_candidate, from_attributes=True
                )
        except IntegrityError as e:
            raise AlreadyExistsError("User already exists") from e

    async def get(self, id: UUID) -> CandidateResponse | None:
        async with self.session_factory() as session:
            result = await session.get(CandidateOrm, id)
            if result is None:
                return None
            return CandidateResponse.model_validate(result, from_attributes=True)

    async def get_by_email(self, email: str) -> CandidateResponse | None:
        async with self.session_factory() as session:
            stmt = select(CandidateOrm).filter_by(email=email)
            res = await session.execute(stmt)
            result = res.scalar_one_or_none()
            if result is None:
                return None
            return CandidateResponse.model_validate(result, from_attributes=True)
