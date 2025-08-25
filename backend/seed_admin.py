import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.hash import bcrypt

from api.models import User, Wallet

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, future=True)
Session = sessionmaker(engine, expire_on_commit=False)


def ensure_admin(email: str, password: str, username: str = "admin"):
    with Session() as db:
        user = db.query(User).filter(User.email == email.lower()).first()
        if not user:
            user = User(
                email=email.lower(),
                username=username,
                password_hash=bcrypt.hash(password),
                is_admin=True,
            )
            db.add(user)
            db.flush()
            db.add(Wallet(user_id=user.id, balance=0))
        else:
            user.is_admin = True
            if password:
                user.password_hash = bcrypt.hash(password)
        db.commit()
        print("Admin listo:", user.email, "id:", user.id)


if __name__ == "__main__":
    ensure_admin(os.getenv("ADMIN_EMAIL","admin@local"), os.getenv("ADMIN_PASSWORD","admin123"))
