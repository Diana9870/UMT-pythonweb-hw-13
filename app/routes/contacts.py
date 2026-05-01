from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ContactCreate, ContactResponse
from app.repository.contacts import *
from app.services.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=list[ContactResponse])
def read_contacts(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return get_contacts(user.id, skip, limit, db)


@router.get("/search")
def search(
    q: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return search_contacts(user.id, q, db)


@router.post("/", response_model=ContactResponse)
def create(
    body: ContactCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return create_contact(body.dict(), user.id, db)


@router.put("/{contact_id}")
def update(
    contact_id: int,
    body: ContactCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    contact = get_contact(contact_id, user.id, db)

    if not contact:
        raise HTTPException(status_code=404)

    return update_contact(contact, body.dict(), db)


@router.delete("/{contact_id}")
def delete(
    contact_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    contact = get_contact(contact_id, user.id, db)

    if not contact:
        raise HTTPException(status_code=404)

    delete_contact(contact, db)

    return {"message": "deleted"}