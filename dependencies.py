from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from config import config
from schemas import AccesTokenData, RefreshTokenData, UserAuth
from security import decode_jwt, oauth2_scheme
from services import (
    ApplicationService,
    CandidateService,
    RefreshTokenService,
    ResumeService,
    UserService,
    VacancyService,
)

SECRET_KEY = config.SECRET_KEY


def get_async_session_factory(req: Request):
    return req.app.state.session_factory  # type: ignore


def get_user_service(
    session_factory: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_async_session_factory)
    ],
) -> UserService:
    return UserService(session_factory)


def get_token_service(
    session_factory: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_async_session_factory)
    ],
) -> RefreshTokenService:
    return RefreshTokenService(session_factory)


def get_application_service(
    session_factory: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_async_session_factory)
    ],
) -> ApplicationService:
    return ApplicationService(session_factory)


def get_candidate_service(
    session_factory: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_async_session_factory)
    ],
) -> CandidateService:
    return CandidateService(session_factory)


def get_resume_service(
    session_factory: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_async_session_factory)
    ],
) -> ResumeService:
    return ResumeService(session_factory)


def get_vacancy_service(
    session_factory: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_async_session_factory)
    ],
) -> VacancyService:
    return VacancyService(session_factory)


def get_refresh_token_from_cookies(request: Request):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token"
        )
    return refresh_token


def get_access_token_data(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> AccesTokenData:
    """Get data from JWT using symmetric key"""
    try:
        payload = decode_jwt(token)
        user_id = payload.get("sub")
        user_role = payload.get("role")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token structure",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return AccesTokenData(user_id=user_id, role=user_role)
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.exceptions.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_refresh_token_data(
    token: Annotated[str, Depends(get_refresh_token_from_cookies)],
) -> RefreshTokenData:
    """Get data from JWT using symmetric key"""
    try:
        payload = decode_jwt(token)
        user_id = payload.get("sub")
        jti = payload.get("jti")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token structure",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return RefreshTokenData(user_id=user_id, jti=jti)
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.exceptions.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_auth_data(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    try:
        return UserAuth(email=form_data.username, password=form_data.password)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.errors()
        )
