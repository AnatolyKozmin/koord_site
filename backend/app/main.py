from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select

from .config import settings
from .database import Base, SessionLocal, engine
from .models import User, UserRole
from .routers import auth, blocks, homework, media, results, users
from .security import hash_password

API_PREFIX = "/api"


def seed_admin() -> None:
    """Создаёт суперадмина при первом запуске, если пользователей ещё нет."""
    with SessionLocal() as db:
        if db.scalar(select(User).limit(1)) is None:
            db.add(
                User(
                    email=settings.admin_email,
                    full_name=settings.admin_name,
                    hashed_password=hash_password(settings.admin_password),
                    role=UserRole.SUPERADMIN,
                )
            )
            db.commit()


def run_migrations() -> None:
    """create_all создаёт только новые таблицы — недостающие колонки доливаем сами."""
    with engine.begin() as conn:
        slide_cols = [row[1] for row in conn.exec_driver_sql("PRAGMA table_info(slides)")]
        if slide_cols and "homework" not in slide_cols:
            conn.exec_driver_sql(
                "ALTER TABLE slides ADD COLUMN homework TEXT NOT NULL DEFAULT ''"
            )


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    run_migrations()
    seed_admin()
    yield


app = FastAPI(title="Koord — обучение координаторов", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# все API-роуты живут под /api — так nginx проксирует /api/* на бэкенд,
# а всё остальное отдаёт как статику SPA
app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(users.router, prefix=API_PREFIX)
app.include_router(blocks.router, prefix=API_PREFIX)
app.include_router(results.router, prefix=API_PREFIX)
app.include_router(homework.router, prefix=API_PREFIX)
app.include_router(media.router, prefix=API_PREFIX)

# статика загруженных картинок
UPLOAD_DIR = Path(settings.upload_dir)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount(f"{API_PREFIX}/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.get(f"{API_PREFIX}/health")
def health():
    return {"status": "ok"}
