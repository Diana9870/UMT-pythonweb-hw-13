from fastapi import APIRouter, Depends, HTTPException
from app.services.auth import decode_token
from app.services.cache import get_cache, set_cache

router = APIRouter(prefix="/users")


def get_current_user(token: str):
    cached = get_cache(token)
    if cached:
        return cached

    user = decode_token(token)
    set_cache(token, user)
    return user


def admin_required(user):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403)


@router.get("/me")
def get_me(user=Depends(get_current_user)):
    return user


@router.get("/admin")
def admin(token: str):
    user = get_current_user(token)
    admin_required(user)
    return {"message": "admin access"}