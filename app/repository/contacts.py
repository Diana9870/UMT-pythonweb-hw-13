from sqlalchemy.orm import Session
from app.models import Contact
from datetime import datetime, timedelta


class ContactsRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_contact(self, body, user):
        contact = Contact(
            first_name=body.first_name,
            last_name=body.last_name,
            email=body.email,
            phone=body.phone,
            birthday=body.birthday,
            user_id=user.id
        )
        self.db.add(contact)
        self.db.commit()
        self.db.refresh(contact)
        return contact

    def get_contacts(self, skip: int, limit: int, user):
        return (
            self.db.query(Contact)
            .filter(Contact.user_id == user.id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_contact_by_id(self, contact_id: int, user):
        return (
            self.db.query(Contact)
            .filter(Contact.id == contact_id, Contact.user_id == user.id)
            .first()
        )

    def update_contact(self, contact_id: int, body, user):
        contact = self.get_contact_by_id(contact_id, user)

        if not contact:
            return None

        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone = body.phone
        contact.birthday = body.birthday

        self.db.commit()
        self.db.refresh(contact)
        return contact

    def delete_contact(self, contact_id: int, user):
        contact = self.get_contact_by_id(contact_id, user)

        if not contact:
            return None

        self.db.delete(contact)
        self.db.commit()
        return contact

    def search_contacts(self, query: str, user):
        return (
            self.db.query(Contact)
            .filter(
                Contact.user_id == user.id,
                Contact.first_name.ilike(f"%{query}%")
                | Contact.last_name.ilike(f"%{query}%")
                | Contact.email.ilike(f"%{query}%"),
            )
            .all()
        )

    def get_upcoming_birthdays(self, user):
        today = datetime.today().date()
        next_week = today + timedelta(days=7)

        contacts = (
            self.db.query(Contact)
            .filter(Contact.user_id == user.id)
            .all()
        )

        result = []
        for c in contacts:
            birthday_this_year = c.birthday.replace(year=today.year)
            if today <= birthday_this_year <= next_week:
                result.append(c)

        return result