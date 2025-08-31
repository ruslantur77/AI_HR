from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from exceptions import AlreadyExistsError
from models import VacancyOrm
from schemas import VacancyResponse


class VacancyService:

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def create(self, title: str, description: str) -> VacancyResponse:
        try:
            async with self.session_factory() as session:
                new_vacancy = VacancyOrm(title=title, description=description)
                session.add(new_vacancy)
                await session.commit()
                await session.refresh(new_vacancy)
                return VacancyResponse.model_validate(new_vacancy, from_attributes=True)
        except IntegrityError as e:
            raise AlreadyExistsError("User already exists") from e

    async def get(self, id: UUID) -> VacancyResponse | None:
        async with self.session_factory() as session:
            result = await session.get(VacancyOrm, id)
            if result is None:
                return None
            return VacancyResponse.model_validate(result, from_attributes=True)

    async def get_all(self) -> list[VacancyResponse]:
        async with self.session_factory() as session:
            result = await session.execute(select(VacancyOrm))
            vacancies = result.scalars().all()
            return [
                VacancyResponse.model_validate(v, from_attributes=True)
                for v in vacancies
            ]
