# Деплой на koordinatorstvo2026.ru

Заменяем старый сайт «Координаторство HR» на это приложение. Схема — ровно как
у старого стека: фронт-контейнер сам раздаёт SPA и проксирует `/api` в бэкенд,
а edge-nginx видит фронт по имени в сети `arkadium_shared`. В конфиге nginx
меняется **одна строка**.

```
Интернет ─▶ edge-nginx (koordinatorstvo2026.ru, TLS, сеть arkadium_shared)
                 │  proxy_pass → koord26-frontend:80
                 ▼
        koord26-frontend (nginx: SPA + /api → бэкенд)   [koord26 + arkadium_shared]
                 │  /api/* → koord26-backend:8000
                 ▼
        koord26-backend (FastAPI, SQLite + uploads в томе)   [koord26]
```

## 1. Код на сервер

```bash
cd ~
git clone <репозиторий> koord26      # или scp/rsync проект целиком
cd koord26
```

## 2. Настроить .env

```bash
cp .env.example .env
nano .env
```

- `SECRET_KEY` — `openssl rand -hex 32`
- `ADMIN_EMAIL` / `ADMIN_PASSWORD` — стартовый суперадмин (создаётся один раз на пустой БД)

Сеть `arkadium_shared` уже прописана в compose как external — трогать не нужно.

## 3. Собрать и поднять

```bash
docker compose build
docker compose up -d
docker compose ps
docker compose logs -f koord26-backend   # ждём "Application startup complete"
```

Проверка, что фронт достаёт бэкенд:

```bash
docker compose exec koord26-frontend wget -qO- http://koord26-backend:8000/api/health
# {"status":"ok"}
```

## 4. Погасить старый сайт

```bash
cd ~/otbor_k
docker compose down          # гасит koord-hr-frontend / backend / redis
```

## 5. Переключить edge-nginx (одна строка)

В `~/infra/nginx.conf`, блок `server_name koordinatorstvo2026.ru`:

```diff
     location / {
-        set $koord_front koord-hr-frontend;
+        set $koord_front koord26-frontend;
         proxy_pass         http://$koord_front:80$request_uri;
```

Применить:

```bash
docker exec <имя_edge_nginx> nginx -t
docker exec <имя_edge_nginx> nginx -s reload
```

## 6. Проверить

https://koordinatorstvo2026.ru — вход под `ADMIN_EMAIL` / `ADMIN_PASSWORD`, затем
курс, редактор блоков, итоги.

## Обновление версии

```bash
cd ~/koord26 && git pull
docker compose build && docker compose up -d
```

## Данные и бэкап

БД `koord.db` и картинки лежат в томе `koord26_data` (`/app/data`), переживают
пересборку.

```bash
docker run --rm -v koord26_data:/data -v "$PWD":/backup alpine \
  tar czf /backup/koord-data-$(date +%F).tar.gz -C /data .
```

## Заметки

- Загрузка видео (до 2 ГБ) требует согласованных лимитов в **трёх** местах:
  бэкенд (`VIDEO_MAX_BYTES` в `media.py` = 2 ГБ), фронт-контейнер
  (`frontend/nginx.conf`, `client_max_body_size 2100M`, уже в репо) и edge-nginx
  на сервере. В `~/infra/nginx.conf`, блок `server_name koordinatorstvo2026.ru`,
  прописать (было 10M):
  ```nginx
  client_max_body_size 2100M;
  location / {
      # ...proxy_pass фронту...
      proxy_request_buffering off;   # стримим гигабайты, не буферизируя на диск edge
      proxy_send_timeout 1800s;
      proxy_read_timeout 1800s;
  }
  ```
  Применить: `docker exec arkadium-edge-nginx nginx -t && docker exec
  arkadium-edge-nginx nginx -s reload` (в `~/infra` **не** `compose up`). Без
  этого edge вернёт 413 ещё до нашего стека.
- Видео лежат в томе `koord26_data` (`/app/data/uploads`) — при файлах на
  гигабайты следить за свободным местом на диске сервера.
- Порты наружу не публикуются — только через edge-nginx.
- Откат: вернуть строку `koord-hr-frontend`, `nginx -s reload`, поднять `~/otbor_k`.
