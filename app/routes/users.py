from fastapi import APIRouter, Depends, HTTPException, status

from app.services.auth import get_current_user
from app.services.roles import require_admin
from app.models import User

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/admin")
async def admin_endpoint(current_user: User = Depends(get_current_user)):
    require_admin(current_user)
    return {"message": "admin access"}