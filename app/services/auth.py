from passlib.context import CryptContext
from jose import jwt
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"])
SECRET_KEY = os.getenv("SECRET_KEY")


def hash_password(password: str):
    """
    Hash password safely (bcrypt limit fix)
    """
    password = password[:72]  
    return pwd_context.hash(password)


def verify_password(plain, hashed):
    """Verify password"""
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict):
    """Create JWT token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")


def decode_token(token: str):
    """Decode JWT"""
    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])