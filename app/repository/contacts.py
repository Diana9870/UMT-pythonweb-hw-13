from sqlalchemy.orm import Session
from app.models import Contact


def get_contacts(user_id: int, skip: int, limit: int, db: Session):
    return db.query(Contact).filter(
        Contact.owner_id == user_id
    ).offset(skip).limit(limit).all()


def search_contacts(user_id: int, query: str, db: Session):
    return db.query(Contact).filter(
        Contact.owner_id == user_id,
        Contact.first_name.ilike(f"%{query}%")
    ).all()


def get_contact(contact_id: int, user_id: int, db: Session):
    return db.query(Contact).filter(
        Contact.id == contact_id,
        Contact.owner_id == user_id
    ).first()


def create_contact(data: dict, user_id: int, db: Session):
    contact = Contact(**data, owner_id=user_id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


def update_contact(contact, data: dict, db: Session):
    for key, value in data.items():
        setattr(contact, key, value)

    db.commit()
    db.refresh(contact)
    return contact


def delete_contact(contact, db: Session):
    db.delete(contact)
    db.commit()