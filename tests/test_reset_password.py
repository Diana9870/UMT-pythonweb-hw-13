import pytest
from fastapi import status
from unittest.mock import AsyncMock

from app.services.reset_password import (
    create_reset_token,
    verify_reset_token,
)


def test_create_reset_token():
    email = "test@example.com"
    token = create_reset_token(email)

    assert isinstance(token, str)
    assert token.count(".") == 2


def test_verify_valid_token():
    email = "test@example.com"
    token = create_reset_token(email)

    assert verify_reset_token(token) == email


def test_verify_invalid_token():
    result = verify_reset_token("invalid.token")
    assert result is None


def test_create_token_invalid_email():
    token = create_reset_token("invalid-email")

    assert verify_reset_token(token) is None


def test_request_password_reset(client, monkeypatch):
    send_email_mock = AsyncMock()

    monkeypatch.setattr(
        "app.services.email.send_email",
        send_email_mock
    )

    response = client.post(
        "/auth/request-password-reset",
        json={"email": "test@example.com"}
    )

    assert response.status_code == status.HTTP_200_OK

    assert send_email_mock.await_count == 1


def test_reset_password_success(client, monkeypatch):
    token = create_reset_token("test@example.com")

    update_mock = AsyncMock()

    monkeypatch.setattr(
        "app.services.auth.update_password",
        update_mock
    )

    response = client.post(
        "/auth/reset-password",
        json={
            "token": token,
            "new_password": "StrongPass123!"
        }
    )

    assert response.status_code == status.HTTP_200_OK

    assert update_mock.await_count == 1


def test_reset_password_invalid_token(client):
    response = client.post(
        "/auth/reset-password",
        json={
            "token": "invalid.token",
            "new_password": "StrongPass123!"
        }
    )

    assert response.status_code in (400, 422)


def test_reset_password_missing_fields(client):
    response = client.post("/auth/reset-password", json={})
    assert response.status_code == 422


def test_reset_password_weak_password(client):
    token = create_reset_token("test@example.com")

    response = client.post(
        "/auth/reset-password",
        json={
            "token": token,
            "new_password": "123"
        }
    )

    assert response.status_code in (400, 422)