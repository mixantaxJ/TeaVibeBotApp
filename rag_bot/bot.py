import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from rag_bot.config import settings
from rag_bot.middlewares.auth import AuthorizationMiddleware
from rag_bot.handlers.errors import router as errors_router
from rag_bot.handlers.admin import router as admin_router
from rag_bot.handlers.user import router as user_router
from rag_bot.core.qdrant import qdrant_manager

logging.basicConfig(level=logging.INFO)

async def main():
    # Initialize bot and storage
    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    redis = Redis.from_url(settings.redis_url)
    storage = RedisStorage(redis=redis)
    dp = Dispatcher(storage=storage)

    # Register middleware
    dp.update.outer_middleware(AuthorizationMiddleware())

    # Include routers (errors should be registered early or at least correctly attached)
    dp.include_router(errors_router)
    dp.include_router(admin_router)
    dp.include_router(user_router)

    # Drop pending updates and start polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
