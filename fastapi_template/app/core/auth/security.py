from datetime import datetime, timedelta
from typing import Optional

from jose import jwt, ExpiredSignatureError
from passlib.context import CryptContext
from pydantic import ValidationError
from starlette import status

from fastapi_template.app.exception.handler import HttpException
from fastapi_template.app.exception.status import ResponseCode
from fastapi_template.app.schema.auth_schema import TokenPayload, TokenResponse
from fastapi_template.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: TokenPayload, expires_delta: timedelta = None) -> TokenResponse:
    if not expires_delta:
        expires_delta = timedelta(seconds=settings.JWT_EXPIRED_SECONDS)
    expire = datetime.utcnow() + expires_delta

    payload = data.dict()
    payload.update({
        "exp": expire,
        'iss': settings.JWT_ISSUER,
        'aud': settings.JWT_AUDIENCE
    })
    encoded_jwt = jwt.encode(
        payload,
        key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    resp_data = {
        "access_token": encoded_jwt,
        "expires_in": expires_delta.total_seconds()
    }
    token_response = TokenResponse(**resp_data)
    return token_response


async def verify_access_token(token: str) -> Optional[TokenPayload]:
    try:
        payload = jwt.decode(token,
                             key=settings.JWT_SECRET_KEY,
                             algorithms=[settings.JWT_ALGORITHM],
                             audience=settings.JWT_AUDIENCE,
                             issuer=settings.JWT_ISSUER)
        if not payload.get("upn"):
            raise HttpException(code=ResponseCode.UNAUTHORIZED, status_code=status.HTTP_401_UNAUTHORIZED)
        token_payload = TokenPayload(**payload)
    except ExpiredSignatureError:
        raise HttpException(code=ResponseCode.TOKEN_EXPIRED, status_code=status.HTTP_401_UNAUTHORIZED)
    except (jwt.JWTError, ValidationError) as e:
        raise HttpException(code=ResponseCode.TOKEN_VALIDATE_FAILED, status_code=status.HTTP_401_UNAUTHORIZED)
    return token_payload


def create_hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
