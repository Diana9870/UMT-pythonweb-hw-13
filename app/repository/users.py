from typing import Optional

from sqlalchemy.orm import Session

from app.models import User


def get_user_by_email(email: str, db: Session) -> Optional[User]:
    """
    Retrieve a user by email.

    :param email: User email address.
    :param db: Database session.
    :return: User object if found, otherwise None.
    """
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(user_id: int, db: Session) -> Optional[User]:
    """
    Retrieve a user by ID.

    :param user_id: User identifier.
    :param db: Database session.
    :return: User object if found, otherwise None.
    """
    return db.query(User).filter(User.id == user_id).first()


def create_user(data: dict, db: Session) -> User:
    """
    Create a new user.

    :param data: Dictionary containing user data.
    :param db: Database session.
    :return: Newly created user.
    """
    user = User(**data)

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def update_user_password(
    email: str,
    hashed_password: str,
    db: Session
) -> bool:
    """
    Update user's password.

    :param email: User email.
    :param hashed_password: New hashed password.
    :param db: Database session.
    :return: True if updated successfully, otherwise False.
    """
    user = get_user_by_email(email, db)

    if not user:
        return False

    user.hashed_password = hashed_password

    db.commit()
    db.refresh(user)

    return True


def update_avatar(
    email: str,
    avatar_url: str,
    db: Session
) -> Optional[User]:
    """
    Update user's avatar.

    :param email: User email.
    :param avatar_url: New avatar URL.
    :param db: Database session.
    :return: Updated user object or None.
    """
    user = get_user_by_email(email, db)

    if not user:
        return None

    user.avatar = avatar_url

    db.commit()
    db.refresh(user)

    return user


def update_role(
    email: str,
    role: str,
    db: Session
) -> Optional[User]:
    """
    Update user role.

    :param email: User email.
    :param role: New role (user/admin).
    :param db: Database session.
    :return: Updated user object or None.
    """
    user = get_user_by_email(email, db)

    if not user:
        return None

    user.role = role

    db.commit()
    db.refresh(user)

    return user


def delete_user(
    email: str,
    db: Session
) -> bool:
    """
    Delete a user from database.

    :param email: User email.
    :param db: Database session.
    :return: True if deleted successfully, otherwise False.
    """
    user = get_user_by_email(email, db)

    if not user:
        return False

    db.delete(user)
    db.commit()

    return True