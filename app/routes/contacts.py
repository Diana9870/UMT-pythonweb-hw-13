from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas import ContactCreate, ContactResponse
from app.repository.contacts import ContactsRepository
from app.services.auth import get_current_user

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=List[ContactResponse])
def read_contacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = ContactsRepository(db)
    return repo.get_contacts(skip, limit, user)


@router.get("/search", response_model=List[ContactResponse])
def search(
    q: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = ContactsRepository(db)
    return repo.search_contacts(q, user)


@router.get("/birthdays", response_model=List[ContactResponse])
def birthdays(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = ContactsRepository(db)
    return repo.get_upcoming_birthdays(user)


@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact_by_id(
    contact_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = ContactsRepository(db)
    contact = repo.get_contact(contact_id, user)

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    return contact


@router.post("/", response_model=ContactResponse)
def create_contact_route(
    body: ContactCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = ContactsRepository(db)
    return repo.create_contact(body, user)


@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact_route(
    contact_id: int,
    body: ContactCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = ContactsRepository(db)
    contact = repo.get_contact(contact_id, user)

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    return repo.update_contact(contact_id, body, user)


@router.delete("/{contact_id}")
def delete_contact_route(
    contact_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = ContactsRepository(db)
    contact = repo.get_contact(contact_id, user)

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    repo.delete_contact(contact_id, user)

    return {"message": "Contact deleted"}