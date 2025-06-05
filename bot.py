import os
import asyncio
import logging

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from handlers import router
from database import init_db


async def main() -> None:
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    init_db()

    active_token_name = os.getenv("ACTIVE_TOKEN")
    if not active_token_name:
        raise RuntimeError("Environment variable ACTIVE_TOKEN is not set")
    bot_token = os.getenv(active_token_name)
    if not bot_token:
        raise RuntimeError(
            f"Environment variable '{active_token_name}' with bot token is not set"
        )
    bot = Bot(bot_token)
    dp = Dispatcher()
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
