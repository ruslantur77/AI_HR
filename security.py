from datetime import datetime, timedelta, timezone

import jwt
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from config import config
from schemas import AccesTokenData, GeneratedToken, RefreshTokenData

ALGORITHM = "HS256"  # симметричный алгоритм
ACCESS_TOKEN_EXPIRE_MINUTES = config.ACCESS_TOKEN_EXPIRE_MINUTES
SECRET_KEY = config.SECRET_KEY  # ваш секрет для HMAC

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def get_hash(password: str) -> str:
    return pwd_context.hash(password)


def generate_token(
    data: dict, headers: dict, expires_delta: timedelta
) -> GeneratedToken:
    """Generate a JWT for provided user data using a symmetric key"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, SECRET_KEY, algorithm=ALGORITHM, headers=headers
    )
    return GeneratedToken(token=encoded_jwt, expiration_time=expire)


def create_access_token(data: AccesTokenData, kid: str) -> GeneratedToken:
    expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return generate_token(
        {"sub": str(data.user_id), "role": data.role.value},
        {"kid": str(kid)},
        expires_delta,
    )


def create_refresh_token(data: RefreshTokenData, kid: str) -> GeneratedToken:
    expires_delta: timedelta = timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS)
    return generate_token(
        {"sub": str(data.user_id), "jti": str(data.jti)},
        {"kid": str(kid)},
        expires_delta,
    )


def decode_jwt(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
