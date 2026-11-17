from datetime import datetime, timedelta, timezone

import jwt

from app.config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

def create_access_token(user_id: int) -> str:
    """Create a signed JWT access token for a user.

    Args:
        user_id (int): Unique identifier of the authenticated user.

    Returns:
        str: Signed JWT containing the user ID and expiration time.
    """
    expires_at = datetime.now(timezone.utc) + timedelta(
        ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expires_at,
    }

    token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )

    return token