import asyncio
import logging
import sys

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from bot.config import (
    BOT_MODE,
    BOT_TOKEN,
    WEBHOOK_HOST,
    WEBHOOK_PATH,
    WEBHOOK_PORT,
    WEBHOOK_URL,
)
from bot.handlers import router

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)


async def run_polling():
    if not BOT_TOKEN:
        raise SystemExit("BOT_TOKEN is required")

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)

    logger.info("Starting bot in polling mode (single instance recommended)")
    await dp.start_polling(bot)


async def run_webhook():
    if not BOT_TOKEN:
        raise SystemExit("BOT_TOKEN is required")
    if not WEBHOOK_URL:
        raise SystemExit("WEBHOOK_URL is required for webhook mode")

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)

    await bot.set_webhook(WEBHOOK_URL)

    app = web.Application()
    webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, WEBHOOK_HOST, WEBHOOK_PORT)
    logger.info("Starting bot webhook on %s:%s%s", WEBHOOK_HOST, WEBHOOK_PORT, WEBHOOK_PATH)
    await site.start()

    while True:
        await asyncio.sleep(3600)


def main():
    if BOT_MODE == "webhook":
        asyncio.run(run_webhook())
    else:
        asyncio.run(run_polling())


if __name__ == "__main__":
    main()
