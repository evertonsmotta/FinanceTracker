from app.database import SessionLocal
from app.models.user import User

def main():
    with SessionLocal() as session:
        user = User(
            name="Test User",
            email="test@exemple.com",
            hashed_password="NOT_A_REAL_PASSWORD_HASH",
        )

        session.add(user)
        session.commit()

        print(f"User created with id: {user.id}")

        saved_user = session.get(User, user.id)

        if saved_user is not None:
            print(f"Name: {saved_user.name}")
            print(f"Email: {saved_user.email}")

if __name__ == "__main__":
    main()