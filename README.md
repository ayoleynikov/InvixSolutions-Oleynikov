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

## Лицензия

Учебный проект для технического задания Invix Solutions.
