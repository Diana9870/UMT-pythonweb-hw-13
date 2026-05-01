from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import UserCreate, UserLogin, Token
from app.services.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    blacklist_token
)
from app.repository.users import get_user_by_email, create_user

router = APIRouter()


@router.post("/register")
def register(body: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_email(body.email, db):
        raise HTTPException(status_code=409, detail="Email exists")

    create_user({
        "username": body.username,
        "email": body.email,
        "hashed_password": hash_password(body.password),
        "confirmed": True
    }, db)

    return {"message": "User created"}


@router.post("/login", response_model=Token)
def login(body: UserLogin, db: Session = Depends(get_db)):
    user = get_user_by_email(body.email, db)

    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access = create_access_token({"sub": user.email})
    refresh = create_refresh_token({"sub": user.email})

    return {
        "access_token": access,
        "refresh_token": refresh
    }


@router.post("/refresh", response_model=Token)
def refresh_token(refresh_token: str):
    payload = decode_token(refresh_token)

    email = payload.get("sub")

    new_access = create_access_token({"sub": email})
    new_refresh = create_refresh_token({"sub": email})

    return {
        "access_token": new_access,
        "refresh_token": new_refresh
    }


@router.post("/logout")
def logout(token: str):
    blacklist_token(token)
    return {"message": "Logged out"}


@router.post("/request-password-reset")
def request_reset(email: EmailSchema):
    token = create_reset_token(email.email)
    send_email(email.email, token)
    return {"message": "Reset email sent"}


@router.post("/reset-password")
def reset_password(data: ResetSchema, db: Session = Depends(get_db)):
    email = verify_reset_token(data.token)
    user = get_user_by_email(db, email)
    user.password = hash_password(data.new_password)
    db.commit()
    return {"message": "Password updated"}