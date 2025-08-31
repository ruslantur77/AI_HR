from uuid import UUID, uuid4

from config import config
from schemas import (
    AccesTokenData,
    RefreshTokenData,
    TokenPair,
    UserRoleEnum,
)
from security import (
    create_access_token,
    create_refresh_token,
    get_hash,
)
from services import RefreshTokenService, UserService

SECRET_KEY = config.SECRET_KEY


def _generate_token_pair(user_id: int):
    jti = uuid4()
    refresh_token = create_refresh_token(
        data=RefreshTokenData(user_id=user_id, jti=jti),
        kid="default",
    )
    refresh_token_hash = get_hash(refresh_token.token)
    access_token = create_access_token(
        data=AccesTokenData(user_id=user_id),
        kid="default",
    )
    return access_token, refresh_token, refresh_token_hash, jti


class CreateTokenPairUseCase:

    def __init__(
        self, token_service: RefreshTokenService, user_service: UserService
    ) -> None:
        self.token_service = token_service
        self.user_service = user_service

    async def execute(self, user_id: UUID) -> TokenPair | None:
        user = await self.user_service.get(user_id)

        if user is None:
            return None

        access_token, refresh_token, refresh_token_hash, jti = _generate_token_pair(
            user.id
        )

        await self.token_service.save(
            jti=jti,
            token_hash=refresh_token_hash,
            expiration_time=refresh_token.expiration_time,
            user_id=user_id,
        )

        return TokenPair(
            access_token=access_token.token,
            refresh_token=refresh_token.token,
        )


class RefreshTokenPairUseCase:

    def __init__(
        self, token_service: RefreshTokenService, user_service: UserService
    ) -> None:
        self.token_service = token_service
        self.user_service = user_service

    async def execute(self, token_data: RefreshTokenData) -> TokenPair | None:
        token = await self.token_service.find_by_jti(jti=token_data.jti)
        if token is None:
            return None

        user = await self.user_service.get(token.user_id)
        if user is None:
            return None

        new_access_token, new_refresh_token, new_refresh_token_hash, jti = (
            _generate_token_pair(user.id)
        )

        await self.token_service.revoke_token(token_data.jti)
        await self.token_service.save(
            jti=jti,
            token_hash=new_refresh_token_hash,
            expiration_time=new_refresh_token.expiration_time,
            user_id=user.id,
        )
        return TokenPair(
            access_token=new_access_token.token,
            refresh_token=new_refresh_token.token,
        )
