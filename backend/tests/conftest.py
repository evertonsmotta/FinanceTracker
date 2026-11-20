import os

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.database import Base

load_dotenv()

@pytest.fixture(scope="session")
def test_engine():
    """Create a database engine for the isolated test database."""
    database_url = os.environ["DATABASE_TEST_URL"]
    parsed_url = make_url(database_url)

    if (
        parsed_url.database != "financetracker_test"
        or parsed_url.port != 5433
        or parsed_url.host not in {"127.0.0.1", "localhost"}
    ):
        raise RuntimeError(
            "Tests must use the isolated financetracker_test database."
        )

    engine = create_engine(database_url, pool_pre_ping=True)

    try:
        with engine.connect() as connection:
            database_name = connection.execute(
                text("SELECT current_database()")
            ).scalar_one()

            if database_name != "financetracker_test":
                raise RuntimeError("Unexpected test database.")

        yield engine
    finally:
        engine.dispose()

@pytest.fixture
def test_db(test_engine):
    """Provide a SQLAlchemy session connected to the test database."""
    with Session(test_engine) as session:
        yield session