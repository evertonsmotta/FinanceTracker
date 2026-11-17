from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

class User(Base):
    """Represent a registered FinanceTracker user.

    Attributes:
        id (int): Unique user identifier.
        name (str): User's display name.
        email (str): Unique email address.
        hashed_password (str): Securely hashed user password.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
