from sqlalchemy.orm import Session
from app.database.models import User


def get_user_by_email(email: str, db: Session):
    """
    Get user by email
    """
    return db.query(User).filter(User.email == email).first()


def create_user(email: str, password: str, db: Session):
    user = User(email=email, password=password, role="user")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user