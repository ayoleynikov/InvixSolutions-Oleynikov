import os


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


BOT_TOKEN = _env("BOT_TOKEN")
ADMIN_TELEGRAM_IDS = {
    int(x.strip())
    for x in _env("ADMIN_TELEGRAM_IDS").split(",")
    if x.strip().isdigit()
}
WEBAPP_URL = _env("WEBAPP_URL", "http://localhost:3000")
API_URL = _env("API_URL", "http://api:8000").rstrip("/")
BOT_MODE = _env("BOT_MODE", "polling").lower()
WEBHOOK_HOST = _env("WEBHOOK_HOST", "0.0.0.0")
WEBHOOK_PORT = int(_env("WEBHOOK_PORT", "8080"))
WEBHOOK_PATH = _env("WEBHOOK_PATH", "/webhook")
WEBHOOK_URL = _env("WEBHOOK_URL")
