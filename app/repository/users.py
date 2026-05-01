from sqlalchemy.orm import Session
from app.models import User


def get_user_by_email(email: str, db: Session):
    return db.query(User).filter(User.email == email).first()


def create_user(data: dict, db: Session):
    user = User(**data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user