from fastapi import APIRouter, Depends, HTTPException
from app.services.auth import decode_token
from app.services.redis_cache import cache
from app.services.roles import require_admin
from app.services.auth import get_current_user
from app.models import User

router = APIRouter(prefix="/users")


def get_current_user(token: str):
    cached = cache.get(token)
    if cached:
        return cached

    user = decode_token(token)
    cache.set(token, user)
    return user


def admin_required(user):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403)


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/admin")
def admin(token: str):
    user = get_current_user(token)
    admin_required(user)
    return {"message": "admin access"}

@router.patch("/avatar")
def update_avatar(data: AvatarUpdate, current_user=Depends(get_current_user)):
    require_admin(current_user)
    return update_avatar_service()