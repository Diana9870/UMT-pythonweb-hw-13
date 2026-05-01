import pytest
from datetime import datetime, timedelta
from jose import jwt

from app.services.auth import (
    hash_password,
    verify_password,
    create_access_token,
)

from app.services.reset_password import (
    create_reset_token,
    verify_reset_token,
)


SECRET_KEY = "test_secret"
ALGORITHM = "HS256"


def test_hash_password_not_equal():
    password = "superpassword"
    hashed = hash_password(password)

    assert hashed != password
    assert isinstance(hashed, str)


def test_verify_password_success():
    password = "superpassword"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_verify_password_fail():
    password = "superpassword"
    hashed = hash_password(password)

    assert verify_password("wrongpassword", hashed) is False


def test_create_access_token_contains_sub():
    data = {"sub": "test@example.com"}
    token = create_access_token(data)

    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert decoded["sub"] == "test@example.com"


def test_access_token_expiration():
    data = {"sub": "test@example.com"}
    token = create_access_token(data)

    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert "exp" in decoded

    exp = datetime.fromtimestamp(decoded["exp"])
    assert exp > datetime.utcnow()


def test_access_token_invalid_signature():
    data = {"sub": "test@example.com"}
    token = create_access_token(data)

    with pytest.raises(Exception):
        jwt.decode(token, "wrong_secret", algorithms=[ALGORITHM])


def test_create_reset_token():
    email = "user@test.com"
    token = create_reset_token(email)

    assert isinstance(token, str)


def test_verify_reset_token_success():
    email = "user@test.com"
    token = create_reset_token(email)

    decoded_email = verify_reset_token(token)

    assert decoded_email == email


def test_verify_reset_token_invalid():
    with pytest.raises(Exception):
        verify_reset_token("invalid.token.here")


def test_reset_token_expired():
    payload = {
        "sub": "user@test.com",
        "exp": datetime.utcnow() - timedelta(minutes=1),
    }

    expired_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(Exception):
        verify_reset_token(expired_token)


def test_create_refresh_token():
     data = {"sub": "user@test.com"}
     token = create_refresh_token(data)

     decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert decoded["sub"] == "user@test.com"
    assert "exp" in decoded