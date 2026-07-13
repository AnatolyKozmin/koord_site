"""Создаёт суперадмина, если его ещё нет.

Запуск: python seed.py [email] [пароль]
По умолчанию: admin@koord.ru / admin123
"""

import sys

from sqlalchemy import select

from app.database import Base, SessionLocal, engine
from app.models import User, UserRole
from app.security import hash_password


def main():
    email = sys.argv[1] if len(sys.argv) > 1 else "admin@koord.ru"
    password = sys.argv[2] if len(sys.argv) > 2 else "admin123"

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        existing = db.scalar(select(User).where(User.email == email))
        if existing:
            print(f"Пользователь {email} уже существует (роль: {existing.role.value})")
            return
        db.add(
            User(
                email=email,
                full_name="Суперадмин",
                hashed_password=hash_password(password),
                role=UserRole.SUPERADMIN,
            )
        )
        db.commit()
        print(f"Суперадмин создан: {email} / {password}")


if __name__ == "__main__":
    main()
