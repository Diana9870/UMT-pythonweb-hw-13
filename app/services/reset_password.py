import logging
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt

from app.config import settings  


logger = logging.getLogger(__name__)

ALGORITHM = "HS256"
RESET_TOKEN_EXPIRE_MINUTES = 15


def create_reset_token(email: str) -> str:
    """
    Generate password reset token.
    """
    payload = {
        "sub": email,
        "type": "reset",
        "exp": datetime.utcnow() + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES),
    }

    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def verify_reset_token(token: str) -> Optional[str]:
    """
    Validate reset token and return email if valid.
    """
    try:
        payload = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
        if payload.get("type") != "reset":
            return None

        return payload.get("sub")

    except JWTError as e:
        logger.warning(f"Invalid or expired reset token: {e}")
        return None