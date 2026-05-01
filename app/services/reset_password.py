from itsdangerous import URLSafeTimedSerializer
import os
from dotenv import load_dotenv

load_dotenv()

serializer = URLSafeTimedSerializer(os.getenv("SECRET_KEY"))


def create_reset_token(email: str):
    """Create reset token"""
    return serializer.dumps(email)


def verify_reset_token(token: str):
    """Verify reset token"""
    try:
        return serializer.loads(token, max_age=3600)
    except:
        return None