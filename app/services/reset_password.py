from datetime import datetime, timedelta, timezone

from email_validator import (
    EmailNotValidError,
    validate_email,
)
from jose import JWTError, jwt

from app.config import settings


RESET_TOKEN_EXPIRE_MINUTES = 15


def create_reset_token(
    email: str,
) -> str | None:
    """
    Create password reset token.

    :param email: User email.
    :return: JWT token or None.
    """

    try:
        validate_email(
            email,
            check_deliverability=False,
        )

    except EmailNotValidError:
        return None

    payload = {
        "sub": email,
        "exp": (
            datetime.now(timezone.utc)
            + timedelta(
                minutes=RESET_TOKEN_EXPIRE_MINUTES
            )
        ),
        "type": "reset",
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def verify_reset_token(
    token: str | None,
) -> str | None:
    """
    Verify password reset token.

    :param token: JWT token.
    :return: User email or None.
    """

    if not token:
        return None

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )

        if payload.get("type") != "reset":
            return None

        email = payload.get("sub")

        if not email:
            return None

        return email

    except JWTError:
        return None
