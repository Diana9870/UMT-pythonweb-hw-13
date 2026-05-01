from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "your_secret"
ALGORITHM = "HS256"


def create_reset_token(email: str):
    payload = {
        "sub": email,
        "exp": datetime.utcnow() + timedelta(minutes=15),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_reset_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])["sub"]