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

app = FastAPI(
    title="Finance Tracker API",
    description="REST API for personal finance management",
    version="1.0.0",
)

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

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
) -> User:
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user

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
