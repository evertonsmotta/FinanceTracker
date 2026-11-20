from sqlalchemy import text
from sqlalchemy.orm import Session

def test_database_connectes_to_test_database(test_db: Session):
    """Verify that the test session useer the expected PostgreSQL database."""
    database_name = test_db.execute(
        text("SELECT current_database()")
    ).scalar_one()

    assert database_name == "financetracker_test"