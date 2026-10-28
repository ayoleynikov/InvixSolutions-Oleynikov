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


def _api_url() -> str:
    raw = _env("API_URL")
    if raw:
        base = raw if raw.startswith("http") else f"http://{raw}"
        return base.rstrip("/")
    host = _env("API_INTERNAL_HOST")
    port = _env("API_INTERNAL_PORT")
    if host and port:
        return f"http://{host}:{port}"
    return "http://api:8000"


API_URL = _api_url()
BOT_MODE = _env("BOT_MODE", "polling").lower()
WEBHOOK_HOST = _env("WEBHOOK_HOST", "0.0.0.0")
WEBHOOK_PATH = _env("WEBHOOK_PATH", "/webhook")
WEBHOOK_PORT = int(_env("WEBHOOK_PORT") or _env("PORT") or "8080")


def _webhook_url() -> str:
    explicit = _env("WEBHOOK_URL")
    if explicit:
        return explicit
    host = _env("RENDER_EXTERNAL_HOSTNAME")
    if host:
        path = WEBHOOK_PATH if WEBHOOK_PATH.startswith("/") else f"/{WEBHOOK_PATH}"
        return f"https://{host}{path}"
    return ""


WEBHOOK_URL = _webhook_url()
