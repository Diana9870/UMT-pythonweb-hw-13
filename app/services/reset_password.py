from datetime import datetime, timedelta, timezone

from email_validator import EmailNotValidError, validate_email
from jose import ExpiredSignatureError, JWTError, jwt

from app.config import settings

ISSUER = "auth-service"
AUDIENCE = "reset"
EXPIRE_MINUTES = 15


def create_reset_token(email: str) -> str | None:
    """
    Create password reset token.

    Args:
        email: User email.

    Returns:
        JWT token or None if email is invalid.
    """

    try:
        validate_email(email)
    except EmailNotValidError:
        return None

    payload = {
        "sub": email,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc)
        + timedelta(minutes=EXPIRE_MINUTES),
        "iss": ISSUER,
        "aud": AUDIENCE,
        "type": "reset",
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def verify_reset_token(token: str) -> str:
    """
    Verify password reset token.

    Args:
        token: JWT token.

    Returns:
        User email.

    Raises:
        JWTError
        ExpiredSignatureError
    """

    payload = jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.algorithm],
        issuer=ISSUER,
        audience=AUDIENCE,
    )

    if payload.get("type") != "reset":
        raise JWTError("Invalid token type")

    email = payload.get("sub")

    if not email:
        raise JWTError("Email not found")

    return email