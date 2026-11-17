from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.security import verify_password
from app.token import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Authenticate a user and return a signed JWT.

    Args:
        form_data (OAuth2PasswordRequestForm):
            OAuth2 credentials submitted as form data.
        db (Session):
            SQLAlchemy database session.

    Returns:
        TokenResponse:
            JWT access token and Bearer token type.

    Raises:
        HTTPException:
            If the supplied credentials are invalid.
    """
    user = db.scalar(
        select(User).where(User.email == form_data.username)
    )

    if user is None or not verify_password(
        form_data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user.id)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )