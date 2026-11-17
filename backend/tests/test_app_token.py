from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.config import JWT_ALGORITHM, JWT_SECRET_KEY
from app.token import create_access_token


def test_create_access_token_contains_user_id():
    """Verify that the JWT contains the expected user identifier."""
    token = create_access_token(user_id=42)

    payload = jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=[JWT_ALGORITHM],
    )

    assert payload["sub"] == "42"
    assert "exp" in payload


def test_decode_rejects_expired_token():
    """Verify that an expired JWT is rejected."""
    payload = {
        "sub": "42",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
    }

    token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )