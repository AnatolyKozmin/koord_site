"""Массовый импорт пользователей из JSON-файла.

Формат JSON — список объектов:
    [{"full_name": "...", "email": "...", "password": "...",
      "team": "...", "role": "coordinator"}, ...]

Идемпотентно: пользователи, у которых email уже есть в базе, пропускаются
(пароль и данные существующих НЕ трогаются). Безопасно запускать повторно.

Запуск локально:
    python import_users.py users_seed.json

Запуск на проде (файл с паролями НЕ в образе — копируем в контейнер):
    docker cp users_seed.json koord26-backend:/app/users_seed.json
    docker exec koord26-backend python import_users.py /app/users_seed.json
"""

import json
import sys

from sqlalchemy import select

from app.database import Base, SessionLocal, engine
from app.models import User, UserRole
from app.security import hash_password


def ensure_team_column() -> None:
    """На случай запуска на старой БД без колонки team (то же, что run_migrations)."""
    with engine.begin() as conn:
        cols = [row[1] for row in conn.exec_driver_sql("PRAGMA table_info(users)")]
        if cols and "team" not in cols:
            conn.exec_driver_sql("ALTER TABLE users ADD COLUMN team VARCHAR(255)")


def main() -> None:
    path = sys.argv[1] if len(sys.argv) > 1 else "users_seed.json"
    with open(path, encoding="utf-8") as f:
        records = json.load(f)

    Base.metadata.create_all(bind=engine)
    ensure_team_column()

    created = 0
    skipped = 0
    with SessionLocal() as db:
        existing = {e.lower() for e in db.scalars(select(User.email)).all()}
        for r in records:
            email = (r["email"] or "").strip()
            if not email:
                print(f"  ПРОПУСК (нет email): {r.get('full_name')!r}")
                skipped += 1
                continue
            if email.lower() in existing:
                skipped += 1
                continue
            db.add(
                User(
                    email=email,
                    full_name=(r["full_name"] or "").strip(),
                    hashed_password=hash_password(r["password"]),
                    role=UserRole(r.get("role", "coordinator")),
                    team=(r.get("team") or None),
                )
            )
            existing.add(email.lower())
            created += 1
        db.commit()

    print(
        f"Готово. Создано: {created}, пропущено (уже были/без email): {skipped}, "
        f"всего в файле: {len(records)}"
    )


if __name__ == "__main__":
    main()
