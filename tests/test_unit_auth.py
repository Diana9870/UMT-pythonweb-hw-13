import pytest
from datetime import datetime
from jose import JWTError, jwt

from app.config import settings
from app.services.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from app.services.reset_password import (
    create_reset_token,
    verify_reset_token,
)


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

    assert verify_password(
        "wrongpassword",
        hashed,
    ) is False


def test_create_access_token_contains_sub():
    data = {"sub": "test@example.com"}

    token = create_access_token(data)

    decoded = jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.algorithm],
    )

    assert decoded["sub"] == "test@example.com"
    assert decoded["type"] == "access"


def test_access_token_expiration():
    data = {"sub": "test@example.com"}

    token = create_access_token(data)

    decoded = jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.algorithm],
    )

    assert "exp" in decoded

    exp = datetime.fromtimestamp(decoded["exp"])

    assert exp > datetime.now()


def test_access_token_invalid_signature():
    token = create_access_token(
        {"sub": "test@example.com"}
    )

    with pytest.raises(JWTError):
        jwt.decode(
            token,
            "wrong_secret",
            algorithms=[settings.algorithm],
        )


def test_create_refresh_token():
    token = create_refresh_token(
        {"sub": "user@test.com"}
    )

    decoded = jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.algorithm],
    )

    assert decoded["sub"] == "user@test.com"
    assert decoded["type"] == "refresh"
    assert "exp" in decoded


def test_create_reset_token():
    email = "user@test.com"

    token = create_reset_token(email)

    assert isinstance(token, str)


def test_verify_reset_token_success():
    email = "user@test.com"

    token = create_reset_token(email)

    result = verify_reset_token(token)

    assert result == email


def test_verify_reset_token_invalid():
    result = verify_reset_token(
        "invalid.token.here"
    )

    assert result is None


def test_verify_reset_token_none():
    result = verify_reset_token(None)

    assert result is None


def test_create_reset_token_invalid_email():
    token = create_reset_token(
        "invalid-email"
    )

    assert token is None
