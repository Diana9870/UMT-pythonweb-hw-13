import logging
from datetime import datetime, timedelta, UTC
from typing import Optional

from jose import JWTError, jwt

from app.config import settings

logger = logging.getLogger(__name__)

ALGORITHM = "HS256"
RESET_TOKEN_EXPIRE_MINUTES = 15

def _create_reset_token(email: str) -> str:
    payload = {
        "sub": email,
        "type": "reset",
        "exp": datetime.now(UTC) + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES),
    }

    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def _verify_reset_token(token: str) -> str:
    payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])

    if payload.get("type") != "reset":
        raise JWTError("Invalid token type")

    return payload.get("sub")

async def create_reset_token(email: str) -> str:
    return _create_reset_token(email)


async def verify_reset_token(token: str) -> Optional[str]:
    try:
        return _verify_reset_token(token)
    except JWTError as e:
        logger.warning(f"Invalid or expired reset token: {e}")
        return None

def create_reset_token_sync(email: str) -> str:
    return _create_reset_token(email)


def verify_reset_token_sync(token: str) -> str:
    return _verify_reset_token(token)