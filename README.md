# Каталог — микросервис INVIX (INV-9H7HH)

MVP каталога товаров: Telegram-бот (aiogram 3), REST API (FastAPI), веб-каталог (Next.js App Router), PostgreSQL и MinIO. Стек поднимается через Docker Compose.

## Архитектура

```
Telegram (бот / Mini App)
        │
        ├── bot ──POST /api/products──► api ◄── GET /api/products ── web (Next.js)
        │                                  │
        │                                  ├── PostgreSQL (товары)
        │                                  └── MinIO S3 (изображения)
        └── WebApp кнопка ───────────────► web «Каталог»
```

- **Состояние** хранится только в PostgreSQL и MinIO. Сервисы `api`, `bot` и `web` не используют локальный диск и in-memory сессии для данных каталога.
- **Масштабирование (2+ реплики):**
  - **api** — горизонтально за балансировщиком; общая БД и bucket MinIO; без sticky sessions.
  - **web** — любое число реплик Next.js (standalone); SSR ходит во внутренний `http://api:8000`.
  - **bot** — для нескольких инстансов задайте `BOT_MODE=webhook`, один публичный `WEBHOOK_URL` за reverse proxy; **polling** (`BOT_MODE=polling`) — только один процесс бота.
  - **postgres / minio** — stateful слой (реплики БД/S3 — отдельная инфраструктура).

## Быстрый старт

1. Скопируйте переменные окружения:

   ```bash
   cp .env.example .env
   ```

2. Укажите в `.env`:
   - `BOT_TOKEN` — токен от [@BotFather](https://t.me/BotFather)
   - `ADMIN_TELEGRAM_IDS` — числовые Telegram ID админов через запятую
   - `WEBAPP_URL` — публичный HTTPS URL страницы каталога (для Mini App в проде; локально можно `http://localhost:3000` для браузера)
   - `MINIO_PUBLIC_URL` — URL, по которому браузер открывает картинки (локально `http://localhost:9000`)

3. Запуск:

   ```bash
   docker compose up --build
   ```

4. Проверка:
   - API: [http://localhost:8000/health](http://localhost:8000/health)
   - Каталог: [http://localhost:3000](http://localhost:3000) — заголовок **«Каталог»**
   - MinIO Console: [http://localhost:9001](http://localhost:9001)

## Функции

| Компонент | Поведение |
|-----------|-----------|
| **Бот** | `/start` или текст → «У меня есть товары» + кнопка WebApp «Открыть каталог» |
| **Админ** | Одно сообщение: **фото + подпись (название)** → загрузка в MinIO, запись в Postgres через API |
| **API** | `GET /health`, `GET /api/products`, `POST /api/products` (multipart: `name`, `image`) |
| **Web** | Страница «Каталог»: список названий и изображений; подключён `telegram-web-app.js` для TMA |

## Структура репозитория

```
api/          FastAPI
bot/          aiogram 3.x
web/          Next.js (App Router)
docker/       init-db.sql, minio-init.sh
docker-compose.yml
.env.example
```

## Локальная разработка без Docker

**API**

```bash
cd api && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql://catalog:catalog_secret@localhost:5432/catalog
uvicorn app.main:app --reload --port 8000
```

**Bot**

```bash
cd bot && pip install -r requirements.txt
export BOT_TOKEN=... ADMIN_TELEGRAM_IDS=... API_URL=http://localhost:8000 WEBAPP_URL=http://localhost:3000
python -m bot.main
```

**Web**

```bash
cd web && npm install && npm run dev
```

## Webhook для нескольких реплик бота

```env
BOT_MODE=webhook
WEBHOOK_URL=https://your-domain.com/webhook
WEBHOOK_PATH=/webhook
WEBHOOK_PORT=8080
```

Пробросьте HTTPS на сервис `bot:8080`. Все реплики получают один и тот же `WEBHOOK_URL`; Telegram шлёт updates на балансировщик.

## Переменные окружения

См. [.env.example](.env.example).

## Деплой на Render

В корне репозитория лежит [`render.yaml`](render.yaml) — Blueprint для PostgreSQL, API, Next.js и Telegram-бота (webhook).

1. Откройте [создание Blueprint](https://dashboard.render.com/blueprint/new?repo=https://github.com/ayoleynikov/InvixSolutions-Oleynikov) и подключите репозitory.
2. При первом применении Blueprint укажите в Dashboard значения с **`sync: false`**:
   - **`BOT_TOKEN`**, **`ADMIN_TELEGRAM_IDS`** — Telegram.
   - **`MINIO_ENDPOINT`**, **`MINIO_ACCESS_KEY`**, **`MINIO_SECRET_KEY`**, **`MINIO_PUBLIC_URL`** — внешнее S3-хранилище (рекомендуется [Cloudflare R2](https://developers.cloudflare.com/r2/) или AWS S3). API использует те же переменные, что и локальный MinIO (`api/app/storage.py`). Создайте bucket `products` (или задайте другое имя в `MINIO_BUCKET` в Blueprint). Для R2: endpoint вида `<account_id>.r2.cloudflarestorage.com`, `MINIO_SECURE=true`, `MINIO_PUBLIC_URL` — публичный URL bucket/CDN для картинок в браузере. Локальный MinIO отдаёт картинки как `{MINIO_PUBLIC_URL}/{MINIO_BUCKET}/{key}`; публичный поддомен R2 `*.r2.dev` уже привязан к bucket, поэтому URL без сегмента bucket: `{MINIO_PUBLIC_URL}/{key}` (определяется автоматически; при необходимости — `MINIO_PUBLIC_URL_OMIT_BUCKET`).
   - **`CORS_ORIGINS`** — HTTPS URL сервиса **web** (например `https://web-xxxx.onrender.com`).
   - **`WEBAPP_URL`** — тот же публичный URL каталога (кнопка Mini App в боте).
   - **`NEXT_PUBLIC_API_URL`** (web) — публичный URL сервиса **api** (например `https://api-xxxx.onrender.com`), если нужен клиентский доступ к API; SSR ходит во внутреннюю сеть через `API_INTERNAL_HOST` / `API_INTERNAL_PORT`.
3. После деплоя проверьте:
   - `https://<api>/health`
   - `https://<web>/`
   - Webhook бота: `https://<bot>/webhook` (задаётся автоматически из `RENDER_EXTERNAL_HOSTNAME`, если `WEBHOOK_URL` не задан).

Сервисы **api**, **web** и **bot** stateless; данные только в Postgres и object storage. Локальный MinIO в Compose на Render не поднимается — только внешний S3-compatible backend.

## Лицензия

Учебный проект для технического задания Invix Solutions.
