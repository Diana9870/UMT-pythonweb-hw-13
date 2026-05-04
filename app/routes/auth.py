from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    UserCreate,
    UserLogin,
    Token,
    RequestPasswordReset,
    ResetPasswordSchema,
)
from app.services.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    blacklist_token,
    update_password,
)
from app.services.reset_password import (
    create_reset_token,
    verify_reset_token,
)
from app.services.email import send_email
from app.repository.users import get_user_by_email, create_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register(body: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_email(body.email, db):
        raise HTTPException(status_code=409, detail="Email exists")

    create_user(
        {
            "username": body.username,
            "email": body.email,
            "hashed_password": hash_password(body.password),
            "confirmed": True,
        },
        db,
    )

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
        "refresh_token": refresh,
    }

@router.post("/refresh", response_model=Token)
def refresh_token(refresh_token: str):
    payload = decode_token(refresh_token)
    email = payload.get("sub")

    return {
        "access_token": create_access_token({"sub": email}),
        "refresh_token": create_refresh_token({"sub": email}),
    }

@router.post("/logout")
def logout(token: str):
    blacklist_token(token)
    return {"message": "Logged out"}

@router.post("/request-password-reset")
async def request_password_reset(body: RequestPasswordReset):
    token = create_reset_token(body.email)

    await send_email(
        body.email,
        "Password reset",
        f"Use this token: {token}"
    )

    return {"message": "Reset email sent"}

@router.post("/reset-password")
async def reset_password(
    body: ResetPasswordSchema,
    db: Session = Depends(get_db),
):
    email = verify_reset_token(body.token)

    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")

    if len(body.new_password) < 6:
        raise HTTPException(status_code=400, detail="Weak password")

    user = get_user_by_email(email, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await update_password(email, body.new_password)

    return {"message": "Password updated"}