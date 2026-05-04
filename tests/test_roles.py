import pytest
from fastapi import HTTPException, status

from app.services.roles import require_admin


class MockUser:
    def __init__(self, role: str):
        self.role = role


def test_require_admin_success():
    user = MockUser(role="admin")

    require_admin(user)


def test_require_admin_forbidden():
    user = MockUser(role="user")

    with pytest.raises(HTTPException) as exc:
        require_admin(user)

    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc.value.detail == "Access denied"


def test_require_admin_no_role():
    class NoRoleUser:
        pass

    user = NoRoleUser()

    with pytest.raises(Exception):
        require_admin(user)


@pytest.mark.asyncio
async def test_admin_can_access_protected_endpoint(client, monkeypatch):
    """
    Імітуємо endpoint з admin-only доступом
    """

    admin_user = MockUser(role="admin")

    async def mock_get_current_user():
        return admin_user

    monkeypatch.setattr(
        "app.routes.auth",
        mock_get_current_user
    )

    response = client.get("/users/me")

    assert response.status_code in (200, 404)  


@pytest.mark.asyncio
async def test_user_cannot_access_admin_endpoint(client, monkeypatch):
    user = MockUser(role="user")

    async def mock_get_current_user():
        return user

    monkeypatch.setattr(
        "app.routes.auth",
        mock_get_current_user
    )

    response = client.get("/users/me")

    assert response.status_code == 403


def test_require_admin_with_none():
    with pytest.raises(Exception):
        require_admin(None)


def test_require_admin_with_invalid_role():
    user = MockUser(role="guest")

    with pytest.raises(HTTPException):
        require_admin(user)