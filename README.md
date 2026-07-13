# Koord — приложение для обучения координаторов

Стек: Vue 3 + Pinia + Vue Router (Vite) / FastAPI + SQLAlchemy + SQLite / JWT-авторизация.

## Роли

| Роль | Права |
|---|---|
| Суперадмин | Управление пользователями и системой |
| Обучающий координатор | Создаёт учебные материалы, обучает; видит список пользователей |
| Координатор | Обучаемый: проходит материалы, видит свой прогресс |

## Запуск

**Бэкенд** (http://localhost:8000, Swagger — /docs):

```powershell
cd backend
python -m venv .venv          # один раз
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python seed.py  # создаёт суперадмина admin@koord.ru / admin123
.venv\Scripts\python -m uvicorn app.main:app --port 8000 --reload
```

**Фронтенд** (http://localhost:5173):

```powershell
cd frontend
npm install
npm run dev
```

## Структура

- `backend/app/models.py` — модель User и enum ролей
- `backend/app/security.py` — bcrypt + JWT (access 30 мин, refresh 7 дней)
- `backend/app/deps.py` — `get_current_user`, `require_roles(...)` для защиты эндпоинтов
- `backend/app/routers/` — `auth` (login/refresh/me), `users` (CRUD, только суперадмин)
- `frontend/src/stores/auth.js` — Pinia-стор авторизации
- `frontend/src/router/index.js` — гарды: редирект на /login, проверка ролей через `meta.roles`
- `frontend/src/api/client.js` — axios с автоподстановкой токена и авто-refresh при 401
