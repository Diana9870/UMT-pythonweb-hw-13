from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.repository.users import get_user_by_email
from app.services.redis_cache import cache

import pickle


SECRET_KEY = "test_secret"
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE = settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE = 60 * 24 * 7 

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str):
    return pwd_context.hash(password)

def create_token(data: dict, expires_delta: int):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(data: dict):
    return create_token(data, ACCESS_TOKEN_EXPIRE)


def create_refresh_token(data: dict):
    return create_token(data, REFRESH_TOKEN_EXPIRE)


def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    if is_token_blacklisted(token):
        raise HTTPException(status_code=401, detail="Token revoked")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        payload = decode_token(token)
        email: str = payload.get("sub")

        if email is None:
            raise credentials_exception

    except Exception:
        raise credentials_exception

    cached_user = await cache.get(email)
    if cached_user:
        return pickle.loads(cached_user)

    user = get_user_by_email(email, db)
    if user is None:
        raise credentials_exception

    await cache.set(email, pickle.dumps(user))

    return user


def get_current_admin(user=Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    return user

_blacklist = set()


def blacklist_token(token: str):
    _blacklist.add(token)


def is_token_blacklisted(token: str) -> bool:
    return token in _blacklist