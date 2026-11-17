from app.security import hash_password, verify_password


def test_hash_password_returns_hash():
    """Verify that the generated hash differs from the original password."""
    password = "MyPassword123"

    hashed = hash_password(password)

    assert hashed != password


def test_verify_password_accepts_correct_password():
    """Verify that the correct password matches its hash."""
    password = "MyPassword123"

    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_verify_password_rejects_incorrect_password():
    """Verify that an incorrect password is rejected."""
    hashed = hash_password("MyPassword123")

    assert verify_password("WrongPassword", hashed) is False


def test_hash_password_generates_unique_hashes():
    """Verify that hashing the same password produces different hashes."""
    password = "MyPassword123"

    hash_one = hash_password(password)
    hash_two = hash_password(password)

    assert hash_one != hash_two