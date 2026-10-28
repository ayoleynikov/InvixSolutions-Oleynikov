# Каталог товаров (INV-9H7HH)

Тестовое задание Invix: Telegram-бот, REST API и веб-каталог. Товары в PostgreSQL, изображения в MinIO (локально) или S3-compatible хранилище на проде (Cloudflare R2, AWS S3).

**Стек:** aiogram 3 · FastAPI · Next.js (App Router) · PostgreSQL · MinIO / S3.

## Запуск

```bash
cp .env.example .env
# BOT_TOKEN — @BotFather; ADMIN_TELEGRAM_IDS — id админов через запятую
# WEBAPP_URL — URL каталога (локально http://localhost:3000)
# MINIO_PUBLIC_URL — откуда браузер тянет картинки (локально http://localhost:9000)
docker compose up --build
```

- API: http://localhost:8000/health  
- Каталог: http://localhost:3000  
- MinIO console: http://localhost:9001  

## Поведение

- Бот: `/start` → «У меня есть товары» и кнопка Mini App «Открыть каталог».
- Админ: одно сообщение **фото + подпись (название)** → API кладёт файл в bucket и строку в Postgres.
- API: `GET /health`, `GET /api/products`, `POST /api/products` (multipart: `name`, `image`).
- Web: страница «Каталог», подключён `telegram-web-app.js`.

Данные каталога только в Postgres и object storage; `api`, `bot`, `web` не пишут их на локальный диск.

## Структура

```
api/          FastAPI
bot/          aiogram 3
web/          Next.js
docker/       init-db.sql, minio-init.sh
docker-compose.yml
render.yaml
.env.example
```

## Переменные окружения

Список и комментарии — [.env.example](.env.example).

## Render

[`render.yaml`](render.yaml) — Blueprint: Postgres, сервисы `api`, `web`, `bot` (webhook). MinIO из compose на Render не поднимается, нужны внешние `MINIO_*`.

1. [Подключить репозиторий](https://dashboard.render.com/blueprint/new?repo=https://github.com/ayoleynikov/InvixSolutions-Oleynikov).
2. В Dashboard задать секреты с `sync: false`: `BOT_TOKEN`, `ADMIN_TELEGRAM_IDS`, `MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`, `MINIO_PUBLIC_URL`, `CORS_ORIGINS` (HTTPS URL web), `WEBAPP_URL`, при необходимости `NEXT_PUBLIC_API_URL` (публичный api). Bucket по умолчанию `products`.
3. R2: endpoint вида `<account_id>.r2.cloudflarestorage.com`, `MINIO_SECURE=true`. Публичный `*.r2.dev` уже привязан к bucket — в URL нет сегмента bucket (логика в `api/app/storage.py`, опция `MINIO_PUBLIC_URL_OMIT_BUCKET`).
4. Проверка: `https://<api>/health`, `https://<web>/`, webhook `https://<bot>/webhook` (если `WEBHOOK_URL` не задан — из `RENDER_EXTERNAL_HOSTNAME`).

SSR web ходит в api по внутренней сети (`API_INTERNAL_HOST` / `API_INTERNAL_PORT` из Blueprint).

## Масштабирование (2+ реплики)

- **api** — stateless, общая БД и bucket, без sticky sessions.
- **web** — сколько угодно реплик Next standalone; SSR на внутренний api.
- **bot** — несколько инстансов только с `BOT_MODE=webhook` и одним `WEBHOOK_URL` за прокси. `polling` — один процесс.
- **postgres / minio** — stateful; реплики — отдельная история.

Webhook:

```env
BOT_MODE=webhook
WEBHOOK_URL=https://your-domain.com/webhook
WEBHOOK_PATH=/webhook
WEBHOOK_PORT=8080
```

HTTPS на `bot:8080`.

## Без Docker (для отладки)

**API:** `cd api`, venv, `pip install -r requirements.txt`,  
`DATABASE_URL=postgresql://catalog:catalog_secret@localhost:5432/catalog`,  
`uvicorn app.main:app --reload --port 8000`.

**Bot:** `cd bot`, `pip install -r requirements.txt`,  
`BOT_TOKEN=... ADMIN_TELEGRAM_IDS=... API_URL=http://localhost:8000 WEBAPP_URL=http://localhost:3000`,  
`python -m bot.main`.

**Web:** `cd web && npm install && npm run dev`.

## Лицензия

Учебный проект по ТЗ Invix Solutions.
