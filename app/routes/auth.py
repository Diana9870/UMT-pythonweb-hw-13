from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Request,
    status,
)
from sqlalchemy.orm import Session

from app.database import get_db
from app.repository.users import (
    create_user,
    get_user_by_email,
)
from app.schemas import (
    RequestPasswordReset,
    ResetPasswordSchema,
    Token,
    UserCreate,
    UserLogin,
)
from app.services.auth import (
    blacklist_token,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    update_password,
    verify_password,
)
from app.services.email import send_email
from app.services.reset_password import (
    create_reset_token,
    verify_reset_token,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.post("/register")

def register(
    body: UserCreate,
    db: Session = Depends(get_db),
):
    """
    Register a new user.

    Creates a new account if the email
    does not already exist.

    :param body: User registration data.
    :param db: Database session.
    :return: Success message.
    """

    existing_user = get_user_by_email(
        body.email,
        db,
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists",
        )

    create_user(
        {
            "username": body.username,
            "email": body.email,
            "hashed_password": hash_password(
                body.password
            ),
            "confirmed": True,
            "role": "user",
        },
        db,
    )

    return {
        "message": "User created successfully"
    }


@router.post(
    "/login",
    response_model=Token,
)
def login(
    body: UserLogin,
    db: Session = Depends(get_db),
):
    """
    Authenticate user.

    Generates access token and refresh token.

    :param body: Login credentials.
    :param db: Database session.
    :return: JWT tokens.
    """

    user = get_user_by_email(
        body.email,
        db,
    )

    if (
        user is None
        or not verify_password(
            body.password,
            user.hashed_password,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token(
        {
            "sub": user.email,
            "role": user.role,
        }
    )

    refresh_token = create_refresh_token(
        {
            "sub": user.email,
            "role": user.role,
        }
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post(
    "/refresh",
    response_model=Token,
)
def refresh(
    refresh_token: str,
):
    """
    Refresh JWT tokens.

    Generates a new access token and
    refresh token using a valid refresh token.

    :param refresh_token: Refresh token.
    :return: New token pair.
    """

    try:
        payload = decode_token(
            refresh_token
        )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        email = payload.get("sub")

        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    return {
        "access_token": create_access_token(
            {"sub": email}
        ),
        "refresh_token": create_refresh_token(
            {"sub": email}
        ),
        "token_type": "bearer",
    }


@router.post("/logout")
async def logout(
    token: str,
):
    """
    Logout user.

    Adds current JWT token
    to Redis blacklist.

    :param token: JWT token.
    :return: Success message.
    """

    await blacklist_token(token)

    return {
        "message": "Successfully logged out"
    }


@router.post(
    "/request-password-reset"
)
async def request_password_reset(
    body: RequestPasswordReset,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Request password reset.

    Generates password reset token and
    sends it to user's email.

    :param body: Email request.
    :param background_tasks: FastAPI background tasks.
    :param request: Current request.
    :param db: Database session.
    :return: Generic success message.
    """

    user = get_user_by_email(
        body.email,
        db,
    )

    if user:

        token = create_reset_token(
            body.email
        )

        reset_link = (
            f"{request.base_url}"
            f"reset-password?token={token}"
        )

        background_tasks.add_task(
            send_email,
            body.email,
            "Password Reset",
            (
                f"Click the link below "
                f"to reset your password:\n\n"
                f"{reset_link}"
            ),
        )

    return {
        "message": (
            "If the email is registered, "
            "password reset instructions have been sent."
        )
    }


@router.post("/reset-password")
async def reset_password(
    body: ResetPasswordSchema,
    db: Session = Depends(get_db),
):
    """
    Reset user password.

    Validates reset token and updates password.

    :param body: Password reset data.
    :param db: Database session.
    :return: Success message.
    """

    email = verify_reset_token(
        body.token
    )

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )

    user = get_user_by_email(
        email,
        db,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if len(body.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least 6 characters",
        )

    await update_password(
        email,
        body.new_password,
        db,
    )

    return {
        "message": "Password updated successfully"
    }