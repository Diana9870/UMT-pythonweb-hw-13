from datetime import date, datetime, timedelta

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import Contact


class ContactsRepository:
    """
    Repository for managing contacts.

    Provides CRUD operations, search functionality,
    and birthday reminders.
    """

    def __init__(self, db: Session):
        """
        Initialize repository.

        :param db: Database session.
        """
        self.db = db

    def create_contact(self, body, user):
        """
        Create a new contact.

        :param body: Contact schema.
        :param user: Current user.
        :return: Created contact.
        """
        contact = Contact(
            first_name=body.first_name,
            last_name=body.last_name,
            email=body.email,
            phone=body.phone,
            birthday=body.birthday,
            user_id=user.id,
        )

        self.db.add(contact)
        self.db.commit()
        self.db.refresh(contact)

        return contact

    def get_contacts(
        self,
        skip: int = 0,
        limit: int = 100,
        user=None,
    ):
        """
        Get all contacts for a user.

        :param skip: Pagination offset.
        :param limit: Pagination limit.
        :param user: Current user.
        :return: List of contacts.
        """

        query = self.db.query(Contact)

        if user:
            query = query.filter(
                Contact.user_id == user.id
            )

        return (
            query
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_contact(
        self,
        contact_id: int,
        user=None,
    ):
        if user:
            return (
                self.db.query(Contact)
                .filter(
                    Contact.id == contact_id,
                    Contact.user_id == user.id,
                )
                .first()
            )

        return (
            self.db.query(Contact)
            .filter(Contact.id == contact_id)
            .first()
        )

    def update_contact(
        self,
        contact_id: int,
        body,
        user=None,
    ):
        """
        Update existing contact.

        :param contact_id: Contact ID.
        :param body: Updated contact data.
        :param user: Current user.
        :return: Updated contact or None.
        """

        contact = self.get_contact(
            contact_id,
            user,
        )

        if contact is None:
            return None

        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone = body.phone
        contact.birthday = body.birthday

        self.db.commit()
        self.db.refresh(contact)

        return contact

    def delete_contact(
        self,
        contact_id: int,
        user=None,
    ):
        """
        Delete contact.

        :param contact_id: Contact ID.
        :param user: Current user.
        :return: Deleted contact or None.
        """

        contact = self.get_contact(
            contact_id,
            user,
        )

        if contact is None:
            return None

        self.db.delete(contact)
        self.db.commit()

        return contact

    def search_contacts(
        self,
        query: str,
        user=None,
    ):
        """
        Search contacts.

        Searches by:
        - first name
        - last name
        - email

        :param query: Search text.
        :param user: Current user.
        :return: Matching contacts.
        """

        db_query = self.db.query(Contact)

        if user:
            db_query = db_query.filter(
                Contact.user_id == user.id
            )

        return (
            db_query.filter(
                or_(
                    Contact.first_name.ilike(
                        f"%{query}%"
                    ),
                    Contact.last_name.ilike(
                        f"%{query}%"
                    ),
                    Contact.email.ilike(
                        f"%{query}%"
                    ),
                )
            )
            .all()
        )

    def get_upcoming_birthdays(
        self,
        user=None,
    ):
        """
        Get contacts whose birthdays occur
        within the next 7 days.

        :param user: Current user.
        :return: List of contacts.
        """

        today = date.today()
        next_week = today + timedelta(days=7)

        query = self.db.query(Contact)

        if user:
            query = query.filter(
                Contact.user_id == user.id
            )

        contacts = query.all()

        upcoming = []

        for contact in contacts:

            birthday = contact.birthday

            if isinstance(
                birthday,
                datetime,
            ):
                birthday = birthday.date()

            birthday_this_year = birthday.replace(
                year=today.year
            )

            if (
                today
                <= birthday_this_year
                <= next_week
            ):
                upcoming.append(contact)

        return upcoming