from schemas.user import (
    UserAuth,
    UserRegisterRequset,
    UserResponse,
)
from security import get_hash, verify_password
from services import UserService


class RegisterUserUseCase:
    def __init__(self, user_service: UserService) -> None:
        self.user_service = user_service

    async def execute(self, data: UserRegisterRequset) -> UserResponse:
        """Register a new user

        Args:
            data (UserRegisterRequset): User's data

        Returns:
            UserResponse: Registered user object
        """
        password_hash = get_hash(data.password)
        res = await self.user_service.create(
            email=data.email, password_hash=password_hash
        )
        return res


class AuthUseCase:
    def __init__(self, user_service: UserService) -> None:
        self.user_service = user_service

    async def execute(self, data: UserAuth) -> UserResponse | None:
        """Authenticates a user using email and password.

        Args:
            data (AuthUserRequest): User's credentials

        Returns:
            UserResponse | None: Authenticated user object if successful, None otherwise
        """
        user = await self.user_service.get_by_email(data.email)
        if not user:
            return None
        if not verify_password(data.password, user.password_hash):
            return None

        return UserResponse.model_validate(user, from_attributes=True)
