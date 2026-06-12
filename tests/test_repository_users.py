from unittest.mock import MagicMock

from app.repository.users import (
    get_user_by_email,
    get_user_by_id,
    update_user_password,
    update_avatar,
    update_role,
    delete_user,
)


def test_get_user_by_email():
    db = MagicMock()

    user = MagicMock()

    db.query().filter().first.return_value = user

    result = get_user_by_email(
        "test@test.com",
        db,
    )

    assert result == user


def test_get_user_by_id():
    db = MagicMock()

    user = MagicMock()

    db.query().filter().first.return_value = user

    result = get_user_by_id(
        1,
        db,
    )

    assert result == user


def test_update_user_password_success():
    db = MagicMock()

    user = MagicMock()

    db.query().filter().first.return_value = user

    result = update_user_password(
        "test@test.com",
        "hashed",
        db,
    )

    assert result is True
    assert user.hashed_password == "hashed"


def test_update_user_password_not_found():
    db = MagicMock()

    db.query().filter().first.return_value = None

    result = update_user_password(
        "test@test.com",
        "hashed",
        db,
    )

    assert result is False


def test_update_avatar():
    db = MagicMock()

    user = MagicMock()

    db.query().filter().first.return_value = user

    result = update_avatar(
        "test@test.com",
        "avatar.jpg",
        db,
    )

    assert result == user
    assert user.avatar == "avatar.jpg"


def test_update_role():
    db = MagicMock()

    user = MagicMock()

    db.query().filter().first.return_value = user

    result = update_role(
        "test@test.com",
        "admin",
        db,
    )

    assert result == user
    assert user.role == "admin"


def test_delete_user_success():
    db = MagicMock()

    user = MagicMock()

    db.query().filter().first.return_value = user

    result = delete_user(
        "test@test.com",
        db,
    )

    assert result is True


def test_delete_user_not_found():
    db = MagicMock()

    db.query().filter().first.return_value = None

    result = delete_user(
        "test@test.com",
        db,
    )

    assert result is False