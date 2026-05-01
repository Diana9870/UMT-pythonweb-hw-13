from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.repository.users import get_user_by_email, create_user
from app.services.auth import hash_password, verify_password, create_access_token
from app.services.reset_password import create_reset_token, verify_reset_token

router = APIRouter(prefix="/auth")


@router.post("/register")
def register(email: str, password: str, db: Session = Depends(get_db)):
    user = get_user_by_email(email, db)
    if user:
        raise HTTPException(status_code=400, detail="User exists")

    return create_user(email, hash_password(password), db)


@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = get_user_by_email(email, db)
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401)

    token = create_access_token({"sub": user.email})
    return {"access_token": token}


@router.post("/reset-request")
def reset_request(email: str):
    token = create_reset_token(email)
    return {"reset_token": token}


@router.post("/reset-password")
def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    email = verify_reset_token(token)
    if not email:
        raise HTTPException(status_code=400)

    user = get_user_by_email(email, db)
    user.password = hash_password(new_password)
    db.commit()

    return {"message": "Password updated"}