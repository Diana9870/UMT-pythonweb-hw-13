from datetime import datetime, timedelta
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

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


ACCESS_TOKEN_EXPIRE = settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE = 60 * 24 * 7  

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    cached_user = await redis_client.get(email)
    if cached_user:
        return pickle.loads(cached_user)

    user = get_user_by_email(db, email)
    if user is None:
        raise credentials_exception

    await redis_client.set(email, pickle.dumps(user), ex=300)

    return user


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str):
    return pwd_context.hash(password)


def create_token(data: dict, expires_delta: int):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )


def create_access_token(data: dict):
    return create_token(data, ACCESS_TOKEN_EXPIRE)


def create_refresh_token(data: dict):
    return create_token(data, REFRESH_TOKEN_EXPIRE)


def decode_token(token: str):
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )


def blacklist_token(token: str):
    r.setex(f"bl:{token}", 3600 * 24, "true")


def is_token_blacklisted(token: str):
    return r.get(f"bl:{token}") is not None


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    if is_token_blacklisted(token):
        raise HTTPException(status_code=401, detail="Token revoked")

    payload = decode_token(token)
    email: Optional[str] = payload.get("sub")

    if email is None:
        raise HTTPException(status_code=401)

    user = get_user_by_email(email, db)

    if not user:
        raise HTTPException(status_code=401)

    return user


def get_current_admin(user=Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403)
    return user


def create_refresh_token(data: dict):
    to_encode = data.copy()
    
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({
        "exp": expire,
        "email": data.get("sub")
    })

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)