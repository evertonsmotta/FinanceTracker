import jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from app.config import JWT_ALGORITHM, JWT_SECRET_KEY
from app.database import get_db
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login"
)

def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db),
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            options={"require": ["sub", "exp"]},
        )

        user_id = int(payload["sub"])

    except (InvalidTokenError, ValueError, TypeError):
        raise credentials_exception from None

    user = db.get(User, user_id)

    if user is None:
        raise credentials_exception

    return user