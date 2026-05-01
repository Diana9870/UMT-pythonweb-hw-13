import pytest
from fastapi import status
from unittest.mock import AsyncMock, patch

from app.services.reset_password import (
    create_reset_token,
    verify_reset_token,
)


@pytest.fixture
def email():
    return "test@example.com"


@pytest.mark.asyncio
async def test_create_reset_token(email):
    token = await create_reset_token(email)

    assert isinstance(token, str)
    assert len(token) > 10


@pytest.mark.asyncio
async def test_verify_valid_token(email):
    token = await create_reset_token(email)

    result = await verify_reset_token(token)

    assert result == email


@pytest.mark.asyncio
async def test_verify_invalid_token():
    token = "invalid.token.value"

    result = await verify_reset_token(token)

    assert result is None


@pytest.mark.asyncio
async def test_verify_expired_token(email, monkeypatch):
    """
    Мокаємо expiration
    """

    token = await create_reset_token(email)

    async def mock_verify(*args, **kwargs):
        return None  

    monkeypatch.setattr(
        "app.services.reset_password",
        mock_verify
    )

    result = await verify_reset_token(token)

    assert result is None


@pytest.mark.asyncio
async def test_request_password_reset(client, monkeypatch, email):
    """
    POST /auth/request-password-reset
    """

    send_email_mock = AsyncMock()

    monkeypatch.setattr(
        "app.services.email.py",
        send_email_mock
    )

    response = await client.post(
        "/auth/request-password-reset",
        json={"email": email}
    )

    assert response.status_code == status.HTTP_200_OK
    send_email_mock.assert_called_once()


@pytest.mark.asyncio
async def test_reset_password_success(client, monkeypatch, email):
    """
    Повний flow reset password
    """

    token = await create_reset_token(email)

    update_password_mock = AsyncMock()

    monkeypatch.setattr(
        "app.repository.users",
        update_password_mock
    )

    response = await client.post(
        "/auth/reset-password",
        json={
            "token": token,
            "new_password": "newStrongPass123"
        }
    )

    assert response.status_code == status.HTTP_200_OK
    update_password_mock.assert_called_once()


@pytest.mark.asyncio
async def test_reset_password_invalid_token(client):
    response = await client.post(
        "/auth/reset-password",
        json={
            "token": "invalid.token",
            "new_password": "password123"
        }
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_reset_password_expired_token(client, monkeypatch, email):
    token = await create_reset_token(email)

    async def mock_verify(*args, **kwargs):
        return None

    monkeypatch.setattr(
        "app.services.reset_password",
        mock_verify
    )

    response = await client.post(
        "/auth/reset-password",
        json={
            "token": token,
            "new_password": "password123"
        }
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
async def test_reset_password_weak_password(client, email):
    token = await create_reset_token(email)

    response = await client.post(
        "/auth/reset-password",
        json={
            "token": token,
            "new_password": "123"
        }
    )

    assert response.status_code in (400, 422)


@pytest.mark.asyncio
async def test_reset_password_missing_fields(client):
    response = await client.post(
        "/auth/reset-password",
        json={}
    )

    assert response.status_code == 422