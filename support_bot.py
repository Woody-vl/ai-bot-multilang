import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from handlers import router

load_dotenv()


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    token = os.getenv("SUPPORT_BOT_TOKEN")
    if not token:
        raise RuntimeError("SUPPORT_BOT_TOKEN is not set")
    bot = Bot(token)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
