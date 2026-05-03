from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import Contact


class ContactsRepository:
    def __init__(self, db: Session):
        self.db = db

    async def get_contacts(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 10
    ) -> List[Contact]:
        return (
            self.db.query(Contact)
            .filter(Contact.owner_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    async def search_contacts(
        self,
        user_id: int,
        query: str
    ) -> List[Contact]:
        return (
            self.db.query(Contact)
            .filter(
                Contact.owner_id == user_id,
                Contact.first_name.ilike(f"%{query}%")
            )
            .all()
        )

    async def get_contact(
        self,
        contact_id: int,
        user_id: int
    ) -> Optional[Contact]:
        return (
            self.db.query(Contact)
            .filter(
                Contact.id == contact_id,
                Contact.owner_id == user_id
            )
            .first()
        )

    async def create_contact(
        self,
        data: dict,
        user_id: int
    ) -> Contact:
        contact = Contact(**data, owner_id=user_id)
        self.db.add(contact)
        self.db.commit()
        self.db.refresh(contact)
        return contact

    async def update_contact(
        self,
        contact: Contact,
        data: dict
    ) -> Contact:
        for key, value in data.items():
            setattr(contact, key, value)

        self.db.commit()
        self.db.refresh(contact)
        return contact

    async def delete_contact(
        self,
        contact: Contact
    ) -> None:
        self.db.delete(contact)
        self.db.commit()