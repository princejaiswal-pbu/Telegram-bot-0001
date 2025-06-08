import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from aiohttp import web

from handlers import start, escrow, admin, payment
from utils.database import init_db
from config import BOT_TOKEN

# Webhook settings
WEBHOOK_PATH = "/webhook"
WEBHOOK_SECRET = "supersecret"  # Secure random string
BASE_WEBHOOK_URL = os.environ.get("WEBHOOK_BASE", "https://telegram-bot-0001-vuiv.onrender.com")
WEBHOOK_URL = f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}"


async def create_bot():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
            protect_content=False
        )
    )
    dp = Dispatcher(storage=MemoryStorage())
    await init_db()

    dp.include_router(start.router)
    dp.include_router(escrow.router)
    dp.include_router(admin.router)
    dp.include_router(payment.router)

    return bot, dp


async def on_startup(app: web.Application):
    bot = app["bot"]
    await bot.set_webhook(WEBHOOK_URL, secret_token=WEBHOOK_SECRET)


async def on_shutdown(app: web.Application):
    bot = app["bot"]
    await bot.delete_webhook()


async def init_app():
    bot, dp = await create_bot()

    app = web.Application()
    app["bot"] = bot

    # Register webhook handler
    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET
    ).register(app, path=WEBHOOK_PATH)

    # Set up webhook lifecycle
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    return app


if __name__ == "__main__":
    port = int(os.environ["PORT"])  # Required for Render
    web.run_app(init_app(), host="0.0.0.0", port=port)
