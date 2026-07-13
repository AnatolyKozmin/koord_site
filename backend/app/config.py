from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    secret_key: str = "dev-secret-change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    database_url: str = "sqlite:///./koord.db"
    upload_dir: str = "uploads"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # авто-сид суперадмина при первом запуске (для деплоя на чистую БД)
    admin_email: str = "admin@koord.ru"
    admin_password: str = "admin123"
    admin_name: str = "Суперадмин"

    class Config:
        env_file = ".env"


settings = Settings()
