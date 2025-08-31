from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from exceptions import AlreadyExistsError
from models import UserOrm
from schemas import UserInDB, UserResponse


class UserService:

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def create(self, email: str, password_hash: str) -> UserResponse:
        try:
            async with self.session_factory() as session:
                new_user = UserOrm(email=email, password_hash=password_hash)
                session.add(new_user)
                await session.commit()
                await session.refresh(new_user)
                return UserResponse.model_validate(new_user, from_attributes=True)
        except IntegrityError as e:
            raise AlreadyExistsError("User already exists") from e

    async def get(self, user_id: UUID) -> UserInDB | None:
        async with self.session_factory() as session:
            result = await session.get(UserOrm, user_id)
            if result is None:
                return None
            return UserInDB.model_validate(result, from_attributes=True)

    async def get_by_email(self, email: str) -> UserInDB | None:
        async with self.session_factory() as session:
            stmt = select(UserOrm).filter_by(email=email)
            result = await session.execute(stmt)
            res = result.scalar()
            if res is None:
                return None
            return UserInDB.model_validate(res, from_attributes=True)
