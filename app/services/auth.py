from datetime import datetime, timedelta, timezone
from typing import Dict

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.repository.users import (
    get_user_by_email,
    update_user_password,
)
from app.services.redis_cache import cache


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """
    Verify password against hash.

    :param plain_password: User password.
    :param hashed_password: Stored password hash.
    :return: True if password is valid.
    """
    return pwd_context.verify(
        plain_password,
        hashed_password
    )


def hash_password(password: str) -> str:
    """
    Generate password hash.

    :param password: Plain text password.
    :return: Hashed password.
    """
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    """
    Create JWT access token.

    :param data: Payload data.
    :return: JWT token.
    """
    to_encode = data.copy()

    expire = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    )

    to_encode.update(
        {
            "exp": expire,
            "type": "access",
        }
    )

    return jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def create_refresh_token(data: dict) -> str:
    """
    Create JWT refresh token.

    :param data: Payload data.
    :return: Refresh JWT token.
    """
    to_encode = data.copy()

    expire = (
        datetime.now(timezone.utc)
        + timedelta(days=7)
    )

    to_encode.update(
        {
            "exp": expire,
            "type": "refresh",
        }
    )

    return jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def decode_token(token: str) -> Dict:
    """
    Decode JWT token.

    :param token: JWT token.
    :return: Decoded payload.
    """
    return jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.algorithm],
    )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Return currently authenticated user.

    User data is cached in Redis
    to reduce database queries.

    :param token: JWT access token.
    :param db: Database session.
    :return: User object.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)

        if payload.get("type") != "access":
            raise credentials_exception

        email = payload.get("sub")

        if email is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    cached_user = await cache.get(
        f"user:{email}"
    )

    if cached_user:
        user = get_user_by_email(email, db)

        if user:
            return user

    user = get_user_by_email(email, db)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    await cache.set(
        f"user:{email}",
        {
            "id": user.id,
            "email": user.email,
            "role": user.role,
        },
        expire=300,
    )

    return user


def get_current_admin(
    current_user=Depends(get_current_user),
):
    """
    Allow access only to administrators.

    :param current_user: Current user.
    :return: User object.
    """

    role = (
        current_user.get("role")
        if isinstance(current_user, dict)
        else current_user.role
    )

    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have enough permissions",
        )

    return current_user


async def update_password(
    email: str,
    new_password: str,
    db: Session,
) -> bool:
    """
    Update user password.

    Password is hashed before saving.
    Redis cache is cleared afterwards.

    :param email: User email.
    :param new_password: New password.
    :param db: Database session.
    :return: True if password updated.
    """

    hashed_password = hash_password(
        new_password
    )

    result = update_user_password(
        email,
        hashed_password,
        db,
    )

    if result:
        await cache.delete(
            f"user:{email}"
        )

    return result


async def blacklist_token(
    token: str
) -> None:
    """
    Add JWT token to blacklist.

    :param token: JWT token.
    """

    await cache.set(
        f"blacklist:{token}",
        "true",
        expire=3600,
    )


async def is_token_blacklisted(
    token: str
) -> bool:
    """
    Check if token is blacklisted.

    :param token: JWT token.
    :return: True if token is blacklisted.
    """

    result = await cache.get(
        f"blacklist:{token}"
    )

    return result is not None