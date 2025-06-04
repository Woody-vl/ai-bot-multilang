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

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    bot = Bot(bot_token)
    dp = Dispatcher()
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
