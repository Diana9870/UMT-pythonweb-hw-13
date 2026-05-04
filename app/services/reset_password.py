from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError, ExpiredSignatureError
import os
from app.config import SECRET_KEY, ALGORITHM

SECRET_KEY = "test_secret"
ALGORITHM = "HS256"

ISSUER = "auth-service"
AUDIENCE = "reset"

EXPIRE_MINUTES = 15


def create_reset_token(email: str) -> str:
    payload = {
        "sub": email,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_MINUTES),
        "iss": ISSUER,
        "aud": AUDIENCE,
        "type": "reset",
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_reset_token(token: str) -> str | None:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            issuer=ISSUER,
            audience=AUDIENCE,
        )

        if payload.get("type") != "reset":
            return None

        return payload.get("sub")

    except (ExpiredSignatureError, JWTError):
        return None