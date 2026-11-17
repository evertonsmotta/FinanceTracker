from fastapi import FastAPI
from fastapi import Depends, HTTPException
from fastapi import status
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse
from app.schemas.user import UserCreate
from app.security import hash_password
from app.routers.auth import router as auth_router
from app.dependencies import get_current_user

app = FastAPI(
    title="Finance Tracker API",
    description="REST API for personal finance management",
    version="1.0.0",
)

app.include_router(auth_router)

@app.get("/")
async def root() -> dict[str,str]:
    return {"message": "Welcome to the Finance Tracker API!"}

@app.get("/health")
async def health_check() -> dict[str,str]:
    return {"status": "ok"}

@app.get("/hello/{name}")
async def hello(name: str) -> dict[str,str]:
    hello_message = f"Hello, {name}!"
    return {"message": hello_message}

@app.get("/users/me", response_model=UserResponse)
def read_current_user(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
) -> User:
    """Return the authenticated user's profile by ID.

    Args:
        user_id (int): Requested user identifier.
        current_user (User): Authenticated user.

    Returns:
        User: Profile of the authenticated user.

    Raises:
        HTTPException: If access to the requested profile is forbidden.
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden",
        )

    return current_user

@app.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
) -> User:
    existing_user = db.scalar(
        select(User).where(User.email == user_data.email)
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=409,
            detail="Email already registered",
        )

    user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
    )

    db.add(user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Email already registared",
        ) from None

    db.refresh(user)
    return user
